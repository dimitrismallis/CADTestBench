import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        base_length = 1.125   # X
        base_width  = 1.5     # Y
        base_height = 0.06    # Z
    
        slot_length = 0.3825  # X
        slot_width  = 0.7575  # Y
        slot_depth  = 0.03    # Z (cut downward from top)
    
        # --- Step 1: Create the base rectangular box ---
        base = cq.Workplane("XY").box(base_length, base_width, base_height)
    
        # --- Step 2: Create the centered slot on the top face ---
        # Use a fresh workplane on the top face, sketch the slot, then cut
        result = (
            base
            .faces(">Z")
            .workplane()
            .center(0, 0)
            .rect(slot_length, slot_width)
            .cutBlind(-slot_depth)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # 1. Bounding box: overall dimensions should still be the base box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - base_length) < TOL, f"X length: expected {base_length}, got {bb.xlen}"
        assert abs(bb.ylen - base_width)  < TOL, f"Y width:  expected {base_width},  got {bb.ylen}"
        assert abs(bb.zlen - base_height) < TOL, f"Z height: expected {base_height}, got {bb.zlen}"
    
        # 2. Volume: base box minus the slot
        base_vol = base_length * base_width * base_height
        slot_vol = slot_length * slot_width * slot_depth
        expected_vol = base_vol - slot_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 1e-4, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # 3. Face count:
        # A box has 6 faces. The slot adds:
        #   - 1 bottom face of the slot (new planar face inside)
        #   - 4 side walls of the slot
        #   - The top face becomes a frame (1 face with inner boundary)
        # Total: 6 - 1 (top) + 1 (top frame) + 4 (slot walls) + 1 (slot bottom) = 11 faces
        face_count = result.faces().size()
        assert face_count == 11, f"Face count: expected 11, got {face_count}"
    
        # 4. The slot bottom face should be at Z = base_height/2 - slot_depth
        #    (since box is centered at Z=0, top is at +base_height/2)
        slot_bottom_z = base_height / 2.0 - slot_depth
        # The slot bottom is the second-highest planar face
        slot_bottom_faces = result.faces(">Z[-2]")
        assert slot_bottom_faces.size() >= 1, "Expected at least one face below the top face"
        slot_face_z = slot_bottom_faces.val().Center().z
        assert abs(slot_face_z - slot_bottom_z) < TOL, \
            f"Slot bottom Z: expected {slot_bottom_z:.4f}, got {slot_face_z:.4f}"
    
        # 5. Verify the slot bottom face dimensions
        slot_bb = slot_bottom_faces.val().BoundingBox()
        assert abs(slot_bb.xlen - slot_length) < TOL, \
            f"Slot face X length: expected {slot_length}, got {slot_bb.xlen}"
        assert abs(slot_bb.ylen - slot_width) < TOL, \
            f"Slot face Y width: expected {slot_width}, got {slot_bb.ylen}"
    
        # 6. Verify the slot is centered (center of slot bottom face should be at x=0, y=0)
        slot_center = slot_bottom_faces.val().Center()
        assert abs(slot_center.x) < TOL, f"Slot center X: expected 0, got {slot_center.x}"
        assert abs(slot_center.y) < TOL, f"Slot center Y: expected 0, got {slot_center.y}"
    
        # 7. Check that a point inside the slot (above slot bottom, below top) is NOT inside the solid
        test_point_in_slot = (0, 0, base_height / 2.0 - slot_depth / 2.0)
        assert not result.val().isInside(test_point_in_slot), \
            f"Point {test_point_in_slot} should be inside the slot (not in solid)"
    
        # 8. Check that a point in the base (below slot depth) IS inside the solid
        test_point_in_base = (0, 0, 0)
        assert result.val().isInside(test_point_in_base), \
            f"Point {test_point_in_base} should be inside the solid base"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00997580/gpt_generated.stl')
