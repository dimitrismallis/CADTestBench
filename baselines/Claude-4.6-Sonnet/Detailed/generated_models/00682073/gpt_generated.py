import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Create the base rectangular block ---
        # 0.75 (X) x 0.5 (Y) x 0.75 (Z), centered at origin
        result = cq.Workplane("XY").box(0.75, 0.5, 0.75)
    
        # --- Step 2: Create the cutout from the top face ---
        # The cutout rectangle is 0.25 (X) x 0.5 (Y), centered in X and Y,
        # aligned with the top edge (top face), extruded downward 0.25 units.
        result = (
            result
            .faces(">Z")          # select top face
            .workplane()          # set workplane on top face
            .center(0, 0)         # center of top face (already centered)
            .rect(0.25, 0.5)      # 0.25 x 0.5 rectangle centered at origin
            .cutBlind(-0.25)      # cut downward 0.25 units
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box: overall shape should still be 0.75 x 0.5 x 0.75
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 0.75) < TOL, f"X length: expected 0.75, got {bb.xlen}"
        assert abs(bb.ylen - 0.50) < TOL, f"Y length: expected 0.50, got {bb.ylen}"
        assert abs(bb.zlen - 0.75) < TOL, f"Z length: expected 0.75, got {bb.zlen}"
    
        # Volume check: base - cutout
        base_vol   = 0.75 * 0.5 * 0.75   # 0.28125
        cutout_vol = 0.25 * 0.5 * 0.25   # 0.03125
        expected_vol = base_vol - cutout_vol  # 0.25
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) < TOL, \
            f"Volume: expected {expected_vol}, got {actual_vol}"
    
        # The cutout should create cylindrical-free geometry — all faces planar
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # Face count: a U-shape from a box with a rectangular cutout
        # Base box has 6 faces; cutout adds: 1 bottom of slot + 2 side walls in X
        # Top face is split into 2 parts (left and right of cutout)
        # Total: 6 - 1 (original top) + 2 (left/right top remnants) + 1 (slot bottom) + 2 (slot X-walls) = 10
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # Verify the cutout depth: the slot bottom should be at Z = 0.375 - 0.25 = 0.125
        # (top face is at Z=0.375, cut goes down 0.25)
        slot_bottom_z = 0.375 - 0.25  # = 0.125
        # The second-highest planar face in Z should be the slot bottom
        # faces(">Z[-2]") gives the second face from top sorted by Z center
        slot_face = result.faces(">Z[-2]")
        slot_face_center = slot_face.val().Center()
        assert abs(slot_face_center.z - slot_bottom_z) < TOL, \
            f"Slot bottom Z: expected {slot_bottom_z}, got {slot_face_center.z}"
    
        # Verify the slot bottom face area: 0.25 x 0.5 = 0.125
        slot_area = slot_face.val().Area()
        assert abs(slot_area - 0.125) < TOL, \
            f"Slot bottom area: expected 0.125, got {slot_area}"
    
        # Verify U-shape: a point inside the cutout should NOT be inside the solid
        # Cutout center is at (0, 0, 0.25) — inside the removed region
        cutout_test_point = (0.0, 0.0, 0.25)
        assert not result.val().isInside(cutout_test_point), \
            f"Point {cutout_test_point} should be outside (in cutout), but is inside"
    
        # A point in the left arm of the U should be inside
        left_arm_point = (-0.3, 0.0, 0.25)
        assert result.val().isInside(left_arm_point), \
            f"Point {left_arm_point} should be inside the left arm of U, but is outside"
    
        # A point in the right arm of the U should be inside
        right_arm_point = (0.3, 0.0, 0.25)
        assert result.val().isInside(right_arm_point), \
            f"Point {right_arm_point} should be inside the right arm of U, but is outside"
    
        # A point in the base of the U (below cutout) should be inside
        base_point = (0.0, 0.0, -0.2)
        assert result.val().isInside(base_point), \
            f"Point {base_point} should be inside the base of U, but is outside"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00682073/gpt_generated.stl')
