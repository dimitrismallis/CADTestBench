import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        L = 1.05964    # main length (X)
        W = 0.56859    # main width (Y)
        H = 0.26362    # main height (Z)
    
        cut_L = 0.206758   # cutout length (X) - stated as ~1/4 of L
        cut_W = W          # cutout width (Y) - same as original
        cut_H = 0.186082   # cutout height (Z) - stated as ~3/4 of H
    
        # --- Step 1: Create the main rectangular prism centered at origin ---
        main = cq.Workplane("XY").box(L, W, H)
    
        # --- Step 2: Create the cutout box ---
        # The cutout is on the RIGHT side (+X side), same width, cut from the top
        # Main prism: X from -L/2 to +L/2, Y from -W/2 to +W/2, Z from -H/2 to +H/2
        # Cutout right face aligns with main right face: cutout X from (L/2 - cut_L) to L/2
        # Cutout top aligns with main top: cutout Z from (H/2 - cut_H) to H/2
        # Cutout spans full width: Y from -W/2 to W/2
    
        # Center of cutout:
        cut_cx = L/2 - cut_L/2          # X center of cutout
        cut_cy = 0.0                     # Y center (full width)
        cut_cz = H/2 - cut_H/2          # Z center (top-aligned)
    
        cutout = cq.Workplane("XY").box(cut_L, cut_W, cut_H).translate((cut_cx, cut_cy, cut_cz))
    
        # --- Step 3: Subtract the cutout from the main prism ---
        result = main.cut(cutout)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box should still be the same as the main prism
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - L) < TOL, f"X length: expected {L}, got {bb.xlen}"
        assert abs(bb.ylen - W) < TOL, f"Y width: expected {W}, got {bb.ylen}"
        assert abs(bb.zlen - H) < TOL, f"Z height: expected {H}, got {bb.zlen}"
    
        # Volume check: main volume minus cutout volume
        main_vol = L * W * H
        cut_vol = cut_L * cut_W * cut_H
        expected_vol = main_vol - cut_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # The cutout is on the right side (+X), so the point inside the cutout region
        # should be OUTSIDE the solid
        # Point inside cutout region (near top-right):
        cutout_test_point = (L/2 - cut_L/4, 0.0, H/2 - cut_H/4)
        assert not result.val().isInside(cutout_test_point, tolerance=1e-5), \
            f"Point {cutout_test_point} should be outside (in cutout region)"
    
        # Point in the lower-right region (below cutout) should be INSIDE
        lower_right_point = (L/2 - cut_L/4, 0.0, -H/4)
        assert result.val().isInside(lower_right_point, tolerance=1e-5), \
            f"Point {lower_right_point} should be inside (below cutout)"
    
        # Point in the left region (not cut) should be INSIDE
        left_point = (-L/4, 0.0, H/4)
        assert result.val().isInside(left_point, tolerance=1e-5), \
            f"Point {left_point} should be inside (left region, not cut)"
    
        # Face count: original box has 6 faces; after L-shaped cut on right side,
        # we expect additional faces. The cutout creates an L-shape cross-section.
        # The right side now has: bottom portion face (right), top cutout face (right),
        # a step face (horizontal), and the inner vertical face.
        # Total faces: 6 original - 1 right face + 4 new faces = 9 faces
        # But let's just check it's more than 6
        face_count = result.faces().size()
        assert face_count >= 8, f"Face count: expected >= 8, got {face_count}"
    
        # Check the cutout region via line intersection
        # A vertical line through the top-right area should intersect fewer faces
        # (the cutout is open at top-right)
        faces_hit = result.val().facesIntersectedByLine(
            (L/2 - cut_L/4, 0.0, H),   # start above the solid
            (0, 0, -1),                  # going down
            direction='AlongAxis'
        )
        # In the cutout region, the line should hit the step face (bottom of cutout)
        # and the bottom face of the main prism
        assert len(faces_hit) >= 1, \
            f"Expected at least 1 face hit in cutout column, got {len(faces_hit)}"
    
        print(f"All assertions passed!")
        print(f"Main volume: {main_vol:.6f}")
        print(f"Cutout volume: {cut_vol:.6f}")
        print(f"Final volume: {actual_vol:.6f}")
        print(f"Face count: {face_count}")
        print(f"Bounding box: {bb.xlen:.5f} x {bb.ylen:.5f} x {bb.zlen:.5f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00031637/gpt_generated.stl')
