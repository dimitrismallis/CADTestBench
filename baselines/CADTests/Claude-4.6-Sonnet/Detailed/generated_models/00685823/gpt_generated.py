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
        L = 0.668421   # length (X)
        W = 0.334211   # width (Y)
        H = 0.668421   # height (Z)
        R = 0.2625 / 2  # radius = 0.13125
    
        # --- Step 1: Build the 2D profile as a closed wire ---
        # The rectangle occupies [0, L] x [0, W]
        # Top-right corner is at (L, W) — circle center placed there
        # Arc goes from (L - R, W) to (L, W - R), quarter circle cut from corner
        # We trace the outline counter-clockwise:
        #   (0, 0) -> (L, 0) -> (L, W-R) [arc start on right edge]
        #   arc through (L - R*sin(45°), W - R + R*cos(45°)) ... 
        #   Actually: arc from (L, W-R) to (L-R, W), center at (L, W)
        #   -> (0, W) -> (0, 0)
    
        # Using CadQuery wire building:
        # Points:
        p0 = (0, 0)
        p1 = (L, 0)
        p2 = (L, W - R)       # arc start (on right edge, going up)
        p3 = (L - R, W)       # arc end (on top edge, going left)
        p4 = (0, W)
    
        # Arc midpoint (on the arc, at 45 degrees from center (L, W)):
        # Center is at (L, W), radius R
        # At 45 degrees (measuring from -X axis toward -Y axis in the corner):
        # angle = 225 degrees from +X axis => point = (L + R*cos(225°), W + R*sin(225°))
        # = (L - R/sqrt(2), W - R/sqrt(2))
        arc_mid = (L - R / math.sqrt(2), W - R / math.sqrt(2))
    
        # Build the profile using Workplane wire operations
        result = (
            cq.Workplane("XY")
            .moveTo(*p0)
            .lineTo(*p1)
            .lineTo(*p2)
            .threePointArc(arc_mid, p3)
            .lineTo(*p4)
            .close()
            .extrude(H)
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Bounding box check
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - L) < TOL, f"X length: expected {L}, got {bb.xlen}"
        assert abs(bb.ylen - W) < TOL, f"Y length: expected {W}, got {bb.ylen}"
        assert abs(bb.zlen - H) < TOL, f"Z length: expected {H}, got {bb.zlen}"
    
        # Volume check: rectangle area minus quarter-circle area, times height
        rect_area = L * W
        quarter_circle_area = math.pi * R**2 / 4
        expected_vol = (rect_area - quarter_circle_area) * H
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count check:
        # Bottom face: 1 (with arc cutout = 1 face)
        # Top face: 1 (with arc cutout = 1 face)
        # Side faces: 4 straight sides + 1 curved (cylindrical) = 5
        # Total: 7 faces
        face_count = result.faces().size()
        assert face_count == 7, f"Face count: expected 7, got {face_count}"
    
        # Check cylindrical face exists (the arc cutout creates a curved surface)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Check the top-right corner is NOT solid (point inside the removed quarter circle)
        # A point at (L - R/4, W - R/4, H/2) should be outside the solid
        test_point_outside = (L - R * 0.3, W - R * 0.3, H / 2)
        solid_shape = result.val()
        is_inside = solid_shape.isInside(test_point_outside)
        assert not is_inside, \
            f"Point {test_point_outside} should be outside (in cutout region), but isInside={is_inside}"
    
        # A point well inside the solid (center-ish area)
        test_point_inside = (L / 4, W / 2, H / 2)
        is_inside2 = solid_shape.isInside(test_point_inside)
        assert is_inside2, \
            f"Point {test_point_inside} should be inside the solid, but isInside={is_inside2}"
    
        # Check bounding box min values (profile starts at origin)
        assert abs(bb.xmin - 0) < TOL, f"xmin: expected 0, got {bb.xmin}"
        assert abs(bb.ymin - 0) < TOL, f"ymin: expected 0, got {bb.ymin}"
        assert abs(bb.zmin - 0) < TOL, f"zmin: expected 0, got {bb.zmin}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00685823/gpt_generated.stl')
