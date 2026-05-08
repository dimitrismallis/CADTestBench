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
        base_length = 200.0   # very long in X
        base_width  = 40.0    # moderate width in Y
        base_height = 5.0     # slight extrusion in Z
    
        # Cutout is ~1/4 the length of the original shape
        cut_length  = base_length / 4   # 50 mm in X
        cut_width   = base_width  / 2   # 20 mm in Y (half the width)
        cut_height  = base_height        # full depth (through cut)
    
        # --- Step 1: Create the base long rectangle (slightly extruded) ---
        # Box centered at origin: X in [-100, 100], Y in [-20, 20], Z in [-2.5, 2.5]
        result = cq.Workplane("XY").box(base_length, base_width, base_height)
    
        # --- Step 2: Create a small rectangular cutout at the bottom-right ---
        # "Bottom-right" = +X side (right), -Y side (bottom)
        # Cutout occupies X in [50, 100] (right quarter), Y in [-20, 0] (bottom half)
        # The cutout is flush with the right face (X=100) and bottom face (Y=-20)
        # Center of cutout in world coords:
        #   X center = base_length/2 - cut_length/2  = 100 - 25 = 75
        #   Y center = -base_width/2 + cut_width/2   = -20 + 10 = -10
        #   Z center = 0 (centered, so cut goes full depth)
    
        cut_x_center = base_length / 2 - cut_length / 2   # 75
        cut_y_center = -base_width  / 2 + cut_width  / 2  # -10
    
        cutout = (
            cq.Workplane("XY")
            .center(cut_x_center, cut_y_center)
            .box(cut_length, cut_width, cut_height)
        )
    
        result = result.cut(cutout)
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # Overall bounding box should still match the base rectangle
        assert abs(bb.xlen - base_length) < TOL, \
            f"X length: expected {base_length}, got {bb.xlen}"
        assert abs(bb.ylen - base_width) < TOL, \
            f"Y length: expected {base_width}, got {bb.ylen}"
        assert abs(bb.zlen - base_height) < TOL, \
            f"Z height: expected {base_height}, got {bb.zlen}"
    
        # Volume check: base volume minus cutout volume
        base_vol     = base_length * base_width * base_height   # 200*40*5 = 40000
        cut_vol      = cut_length  * cut_width  * cut_height    # 50*20*5  = 5000
        expected_vol = base_vol - cut_vol                       # 35000
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Cutout is 1/4 the length of the original shape
        assert abs(cut_length - base_length / 4) < TOL, \
            f"Cutout length should be 1/4 of base: expected {base_length/4}, got {cut_length}"
    
        # The cutout should be on the right side: check that a point inside the
        # cutout region is NOT inside the solid
        cutout_interior = (cut_x_center, cut_y_center, 0.0)
        assert not result.val().isInside(cutout_interior), \
            f"Point {cutout_interior} should be inside the cutout (not in solid)"
    
        # A point in the left half of the base should still be inside the solid
        interior_point = (-50.0, 0.0, 0.0)
        assert result.val().isInside(interior_point), \
            f"Point {interior_point} should be inside the solid"
    
        # A point in the top-right (not cut) region should still be inside the solid
        top_right_point = (75.0, 10.0, 0.0)   # Y=10 is the top half, not cut
        assert result.val().isInside(top_right_point), \
            f"Point {top_right_point} should be inside the solid (top-right, not cut)"
    
        # Face count reasoning:
        # The cutout is flush with the right face (X=100) and bottom-Y face (Y=-20),
        # so those two faces are simply trimmed (not split). The top and bottom Z faces
        # each get an L-shaped notch but remain single planar faces.
        # New inner walls added by cutout: left wall (at X=50) + back wall (at Y=0) = 2
        # Total: 6 original faces + 2 new inner walls = 8 faces
        face_count = result.faces().size()
        assert face_count == 8, \
            f"Face count: expected 8, got {face_count}"
    
        # Confirm only planar faces (no cylinders)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, \
            f"Cylindrical faces: expected 0, got {cyl_faces}"
    
        print(f"All assertions passed!")
        print(f"  Bounding box: {bb.xlen} x {bb.ylen} x {bb.zlen}")
        print(f"  Volume: {actual_vol:.1f} (expected {expected_vol:.1f})")
        print(f"  Face count: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00997068/gpt_generated.stl')
