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
        L = 80.0   # length (X)
        W = 20.0   # width (Y)
        H = 20.0   # height (Z)
    
        cut_L = L / 4       # 20.0  (1/4 length)
        cut_W = W           # 20.0  (same width)
        cut_H = H * 3 / 4  # 15.0  (3/4 height)
    
        # --- Step 1: Create the long rectangular prism centered at origin ---
        # Box centered at (0, 0, 0): X from -40 to 40, Y from -10 to 10, Z from -10 to 10
        result = cq.Workplane("XY").box(L, W, H)
    
        # --- Step 2: Cut out a small rectangular prism from the right side ---
        # The cutout is on the right side (max X), full width (Y), 3/4 height.
        # The box is centered at origin, so right side is at x=40.
        # Cutout spans: X from 20 to 40 (last 1/4 of length)
        #               Y from -10 to 10 (full width)
        #               Z from -10 to 5  (3/4 height from bottom)
        # Center of cutout box: x = (20+40)/2 = 30, y = 0, z = (-10+5)/2 = -2.5
        cut_x_center = (L/2 - cut_L/2)          # 40 - 10 = 30
        cut_y_center = 0.0
        cut_z_center = -H/2 + cut_H/2           # -10 + 7.5 = -2.5
    
        cutter = cq.Workplane("XY").box(cut_L, cut_W, cut_H).translate(
            (cut_x_center, cut_y_center, cut_z_center)
        )
    
        result = result.cut(cutter)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box: overall shape still spans full L x W x H
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - L) < TOL, f"X length: expected {L}, got {bb.xlen}"
        assert abs(bb.ylen - W) < TOL, f"Y length: expected {W}, got {bb.ylen}"
        assert abs(bb.zlen - H) < TOL, f"Z length: expected {H}, got {bb.zlen}"
    
        # Volume check:
        # Original volume = L * W * H = 80 * 20 * 20 = 32000
        # Cutout volume   = cut_L * cut_W * cut_H = 20 * 20 * 15 = 6000
        # Expected volume = 32000 - 6000 = 26000
        original_vol = L * W * H
        cutout_vol   = cut_L * cut_W * cut_H
        expected_vol = original_vol - cutout_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) < 1.0, \
            f"Volume: expected {expected_vol}, got {actual_vol}"
    
        # The cutout is on the right side: check that a point inside the cutout region is NOT inside the solid
        # Cutout region center: (30, 0, -2.5) — should be empty (outside solid)
        solid_shape = result.val()
        cutout_interior = (30.0, 0.0, -2.5)
        assert not solid_shape.isInside(cutout_interior), \
            f"Point {cutout_interior} should be inside the cutout (empty), but it's inside the solid"
    
        # A point in the left portion of the prism should be inside the solid
        left_interior = (-30.0, 0.0, 0.0)
        assert solid_shape.isInside(left_interior), \
            f"Point {left_interior} should be inside the solid, but it's not"
    
        # A point in the top-right area (above the cutout) should still be inside the solid
        top_right_interior = (30.0, 0.0, 8.0)
        assert solid_shape.isInside(top_right_interior), \
            f"Point {top_right_interior} should be inside the solid (above cutout), but it's not"
    
        # Check that the cutout does NOT go all the way to the top (only 3/4 height)
        # The top of the cutout is at z = -10 + 15 = 5, so z=7 on the right side should be solid
        above_cutout = (30.0, 0.0, 7.0)
        assert solid_shape.isInside(above_cutout), \
            f"Point {above_cutout} should be inside the solid (above cutout top), but it's not"
    
        # The cutout bottom matches the prism bottom, so z=-9 on the right side should be empty
        inside_cutout_bottom = (30.0, 0.0, -9.0)
        assert not solid_shape.isInside(inside_cutout_bottom), \
            f"Point {inside_cutout_bottom} should be in the cutout (empty), but it's inside the solid"
    
        print(f"All assertions passed!")
        print(f"  Bounding box: {bb.xlen} x {bb.ylen} x {bb.zlen}")
        print(f"  Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00031637/gpt_generated.stl')
