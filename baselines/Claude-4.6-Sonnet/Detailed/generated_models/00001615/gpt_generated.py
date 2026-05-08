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
        cyl_height = 1.5
        cyl_diameter = 0.6
        cyl_radius = cyl_diameter / 2  # 0.3
    
        cut_length = 0.235   # along X
        cut_width = 0.6      # along Y (full diameter)
        cut_height = 0.292   # depth of cut along Z
    
        # --- Step 1: Create the base cylinder centered at origin ---
        # Cylinder centered at (0,0,0), so top face is at Z = cyl_height/2 = 0.75
        result = cq.Workplane("XY").cylinder(cyl_height, cyl_radius)
    
        # --- Step 2: Create the rectangular cut box ---
        # The cut starts at the top center (Z = 0.75) and extends downward by cut_height.
        # Box center Z = 0.75 - cut_height/2
        cut_z_center = cyl_height / 2 - cut_height / 2  # 0.75 - 0.146 = 0.604
    
        cut_box = (
            cq.Workplane("XY")
            .box(cut_length, cut_width, cut_height, centered=True)
            .translate((0, 0, cut_z_center))
        )
    
        # --- Step 3: Subtract the cut box from the cylinder ---
        result = result.cut(cut_box)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Check bounding box: cylinder diameter = 0.6, height = 1.5
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - cyl_diameter) < TOL, f"BBox X: expected {cyl_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - cyl_diameter) < TOL, f"BBox Y: expected {cyl_diameter}, got {bb.ylen}"
        assert abs(bb.zlen - cyl_height) < TOL, f"BBox Z: expected {cyl_height}, got {bb.zlen}"
    
        # Check Z extents: bottom at -0.75, top at 0.75
        assert abs(bb.zmin - (-cyl_height / 2)) < TOL, f"BBox zmin: expected {-cyl_height/2}, got {bb.zmin}"
        assert abs(bb.zmax - (cyl_height / 2)) < TOL, f"BBox zmax: expected {cyl_height/2}, got {bb.zmax}"
    
        # Volume check:
        # Full cylinder volume minus the cut volume (the cut is fully inside the cylinder)
        cyl_vol = math.pi * cyl_radius**2 * cyl_height
        # The cut box is 0.235 x 0.6 x 0.292, but it's clipped by the cylinder boundary.
        # The cut width (0.6) equals the diameter, so the box extends from -0.3 to +0.3 in Y.
        # The cut length (0.235) is less than the diameter (0.6), so it's fully inside in X.
        # The actual removed volume is the intersection of the box with the cylinder.
        # Since cut_length (0.235) < diameter (0.6), the box in X goes from -0.1175 to +0.1175.
        # In Y, the box goes from -0.3 to +0.3 (full diameter), clipped by cylinder.
        # We need to compute the intersection volume numerically.
        # For a rectangle [-0.1175, 0.1175] x [-0.3, 0.3] intersected with circle r=0.3:
        # Since x range is [-0.1175, 0.1175] and r=0.3, for each x in that range,
        # y goes from -sqrt(r^2 - x^2) to +sqrt(r^2 - x^2), but capped at ±0.3.
        # Since r=0.3, at x=0.1175, y_max = sqrt(0.09 - 0.01381) = sqrt(0.07619) ≈ 0.276
        # So the y extent is always less than 0.3 for |x| > 0, meaning the box in Y is NOT
        # fully inside the cylinder everywhere. Let's compute numerically.
    
        # Numerical integration for intersection area
        n_samples = 10000
        x_vals = np.linspace(-cut_length/2, cut_length/2, n_samples)
        dx = x_vals[1] - x_vals[0]
        intersection_area = 0.0
        for x in x_vals:
            y_cyl = math.sqrt(max(0, cyl_radius**2 - x**2))
            y_box = cut_width / 2
            y_intersect = min(y_cyl, y_box)
            intersection_area += 2 * y_intersect * dx
    
        cut_vol_actual = intersection_area * cut_height
        expected_vol = cyl_vol - cut_vol_actual
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.5f}, got {actual_vol:.5f}"
    
        # Check that the cut is present: a point inside the cut region should be OUTSIDE the solid
        # Cut region: x=0, y=0, z = top - cut_height/2 = 0.604 (inside the cut)
        cut_center_point = (0, 0, cut_z_center)
        assert not result.val().isInside(cut_center_point), \
            f"Point {cut_center_point} should be outside (in the cut region)"
    
        # Check that a point in the cylinder body (below the cut) is INSIDE the solid
        body_point = (0, 0, 0)  # center of cylinder
        assert result.val().isInside(body_point), \
            f"Point {body_point} should be inside the cylinder body"
    
        # Check that the top face has been modified (cut creates additional faces)
        # The original cylinder has 3 faces: top circle, bottom circle, curved side
        # After cut: the top is split, and we get additional planar faces from the cut
        n_faces = result.faces().size()
        assert n_faces > 3, f"Expected more than 3 faces after cut, got {n_faces}"
    
        # Check cylindrical face still exists
        n_cyl_faces = result.faces("%Cylinder").size()
        assert n_cyl_faces >= 1, f"Expected at least 1 cylindrical face, got {n_cyl_faces}"
    
        # Check there is exactly 1 solid
        n_solids = result.solids().size()
        assert n_solids == 1, f"Expected 1 solid, got {n_solids}"
    
        print(f"All assertions passed!")
        print(f"Cylinder volume: {cyl_vol:.5f}")
        print(f"Cut volume (actual intersection): {cut_vol_actual:.5f}")
        print(f"Expected final volume: {expected_vol:.5f}")
        print(f"Actual final volume: {actual_vol:.5f}")
        print(f"Number of faces: {n_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00001615/gpt_generated.stl')
