import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        plate_width  = 40.0   # X dimension
        plate_height = 60.0   # Z dimension (height); width ~ 2/3 of height: 40/60 = 2/3
        plate_depth  = 10.0   # Y dimension (depth/thickness)
    
        slot_width   = 8.0    # X dimension of the slot (small rectangle)
        slot_height  = plate_height  # Z dimension: runs full height bottom to top
    
        # --- Step 1: Create the base rectangular plate ---
        # Box centered at origin: X=[-20,20], Y=[-5,5], Z=[-30,30]
        result = cq.Workplane("XY").box(plate_width, plate_depth, plate_height)
    
        # --- Step 2: Select the front face (minimum Y face) and create a workplane ---
        # On this face, sketch a small rectangle centered horizontally (X=0),
        # running full height (Z from -30 to 30), then cut all the way through.
        result = (
            result
            .faces("<Y")               # front face at minimum Y
            .workplane()               # workplane on the front face
            .rect(slot_width, slot_height)   # small rectangle: 8 wide, 60 tall (full height)
            .cutThruAll()              # cut through the full depth
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box should still match the plate dimensions
        assert abs(bb.xlen - plate_width)  < TOL, f"X length: expected {plate_width}, got {bb.xlen}"
        assert abs(bb.ylen - plate_depth)  < TOL, f"Y length: expected {plate_depth}, got {bb.ylen}"
        assert abs(bb.zlen - plate_height) < TOL, f"Z length: expected {plate_height}, got {bb.zlen}"
    
        # Width-to-height ratio check: width ~ 2/3 of height
        ratio = plate_width / plate_height
        assert abs(ratio - 2/3) < TOL, f"Width/Height ratio: expected {2/3:.4f}, got {ratio:.4f}"
    
        # Volume check: plate volume minus slot volume
        plate_vol = plate_width * plate_depth * plate_height
        slot_vol  = slot_width * plate_depth * slot_height
        expected_vol = plate_vol - slot_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # A plain box has 6 faces; the slot adds inner faces so net face count > 6
        face_count = result.faces().size()
        assert face_count > 6, f"Face count: expected > 6 (slot adds faces), got {face_count}"
    
        # Check the slot exists: a point inside the slot region should be OUTSIDE the solid
        # Slot center is at (0, 0, 0) — inside the slot void
        solid = result.val()
        slot_center_point = (0.0, 0.0, 0.0)
        assert not solid.isInside(slot_center_point), \
            f"Point {slot_center_point} should be outside (in the slot void), but isInside returned True"
    
        # Check that a point in the solid body (not in the slot) is inside
        # e.g., at X=15 (away from slot), Y=0, Z=0
        body_point = (15.0, 0.0, 0.0)
        assert solid.isInside(body_point), \
            f"Point {body_point} should be inside the solid body, but isInside returned False"
    
        # Check symmetry: center of mass should be near (0, 0, 0) due to symmetric slot
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"Center of mass X: expected ~0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected ~0, got {com.y}"
        assert abs(com.z) < TOL, f"Center of mass Z: expected ~0, got {com.z}"
    
        # Verify the slot goes all the way through (front to back):
        # A line along Y through the slot center (X=0, Z=0) should intersect 0 faces
        faces_hit = solid.facesIntersectedByLine((0, -10, 0), (0, 1, 0))
        assert len(faces_hit) == 0, \
            f"Line through slot center should hit 0 faces (open slot), but hit {len(faces_hit)}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00996962/gpt_generated.stl')
