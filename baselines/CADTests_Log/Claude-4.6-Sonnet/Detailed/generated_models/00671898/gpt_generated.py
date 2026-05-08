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
        base_length = 0.676776   # total X span
        base_width  = 0.20312    # base thickness (Y direction in profile, or Z base height)
    
        # Heights of peaks and troughs (Z values above base)
        h_peak1   = 0.102138   # peak of first (left) triangle
        h_trough1 = 0.059507   # trough between first and second
        h_peak2   = 0.135891   # peak of second (center) triangle
        h_trough2 = 0.057730   # trough between second and third
        h_peak3   = 0.089704   # peak of third (right) triangle
    
        extrude_depth = 0.75   # extrusion depth
        translate_x   = -0.349931  # translation along X
    
        # --- Step 1: Define X positions for the mountain profile ---
        # Divide base into 6 equal segments: base_left, peak1, trough1, peak2, trough2, peak3, base_right
        dx = base_length / 6.0
        x0 = 0.0              # base left
        x1 = dx               # peak 1
        x2 = 2 * dx           # trough 1-2
        x3 = 3 * dx           # peak 2 (center)
        x4 = 4 * dx           # trough 2-3
        x5 = 5 * dx           # peak 3
        x6 = base_length      # base right
    
        # --- Step 2: Define the 2D profile points in XZ plane ---
        # The profile is a closed polygon:
        # Bottom-left -> bottom-right (base) -> up through mountain profile -> back to start
        # Base is at z=0, mountains go up in Z
        # We include a base rectangle of height base_width below z=0
    
        # Profile points (going clockwise when viewed from front):
        # Start at bottom-left corner, go right along bottom, up the right side,
        # then trace the mountain profile from right to left, then down the left side
    
        # Actually, let's go counter-clockwise (standard for extrusion):
        # Bottom-left (0, -base_width) -> bottom-right (base_length, -base_width) ->
        # right base (base_length, 0) -> peak3 -> trough2 -> peak2 -> trough1 -> peak1 ->
        # left base (0, 0) -> back to bottom-left
    
        # Using XY plane for the profile (X = horizontal, Y = vertical/height)
        # Then extrude in Z direction
    
        profile_pts = [
            (x0, -base_width),   # bottom-left
            (x6, -base_width),   # bottom-right
            (x6, 0.0),           # right base top
            (x5, h_peak3),       # peak 3
            (x4, h_trough2),     # trough 2-3
            (x3, h_peak2),       # peak 2 (center)
            (x2, h_trough1),     # trough 1-2
            (x1, h_peak1),       # peak 1
            (x0, 0.0),           # left base top
        ]
    
        # --- Step 3: Create the 2D profile as a closed wire and extrude ---
        # Build the profile using lineTo commands in XY plane
        result = (
            cq.Workplane("XY")
            .moveTo(profile_pts[0][0], profile_pts[0][1])
            .lineTo(profile_pts[1][0], profile_pts[1][1])
            .lineTo(profile_pts[2][0], profile_pts[2][1])
            .lineTo(profile_pts[3][0], profile_pts[3][1])
            .lineTo(profile_pts[4][0], profile_pts[4][1])
            .lineTo(profile_pts[5][0], profile_pts[5][1])
            .lineTo(profile_pts[6][0], profile_pts[6][1])
            .lineTo(profile_pts[7][0], profile_pts[7][1])
            .lineTo(profile_pts[8][0], profile_pts[8][1])
            .close()
            .extrude(extrude_depth)
        )
    
        # --- Step 4: Translate along X axis ---
        result = result.translate((translate_x, 0, 0))
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Check bounding box
        bb = result.val().BoundingBox()
    
        # X extent: base_length + translate_x to translate_x (since original x goes 0 to base_length)
        expected_xmin = translate_x  # 0 + translate_x
        expected_xmax = translate_x + base_length  # base_length + translate_x
        assert abs(bb.xmin - expected_xmin) < TOL, f"xmin: expected {expected_xmin:.6f}, got {bb.xmin:.6f}"
        assert abs(bb.xmax - expected_xmax) < TOL, f"xmax: expected {expected_xmax:.6f}, got {bb.xmax:.6f}"
        assert abs(bb.xlen - base_length) < TOL, f"xlen: expected {base_length:.6f}, got {bb.xlen:.6f}"
    
        # Y extent: extrude_depth (from 0 to extrude_depth in Z after extrusion in XY plane)
        # When we extrude in XY plane, extrusion goes in Z direction
        assert abs(bb.zlen - extrude_depth) < TOL, f"zlen (extrude): expected {extrude_depth:.6f}, got {bb.zlen:.6f}"
    
        # Y extent: from -base_width to h_peak2 (max height)
        expected_ymin = -base_width
        expected_ymax = h_peak2
        assert abs(bb.ymin - expected_ymin) < TOL, f"ymin: expected {expected_ymin:.6f}, got {bb.ymin:.6f}"
        assert abs(bb.ymax - expected_ymax) < TOL, f"ymax: expected {expected_ymax:.6f}, got {bb.ymax:.6f}"
        assert abs(bb.ylen - (base_width + h_peak2)) < TOL, f"ylen: expected {base_width + h_peak2:.6f}, got {bb.ylen:.6f}"
    
        # Volume check: approximate (profile area * extrude_depth)
        # Profile area = base rectangle + mountain area above z=0
        # Base rectangle area = base_length * base_width
        # Mountain area (trapezoids between consecutive points):
        # Using shoelace formula for the polygon above z=0
        pts_above = [(x0, 0), (x1, h_peak1), (x2, h_trough1), (x3, h_peak2), 
                     (x4, h_trough2), (x5, h_peak3), (x6, 0)]
        # Shoelace for the full profile polygon
        all_pts = profile_pts + [profile_pts[0]]  # close
        area = 0
        for i in range(len(profile_pts)):
            j = (i + 1) % len(profile_pts)
            area += profile_pts[i][0] * profile_pts[j][1]
            area -= profile_pts[j][0] * profile_pts[i][1]
        profile_area = abs(area) / 2.0
        expected_vol = profile_area * extrude_depth
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that the object has planar faces (it's a prism)
        n_planar = result.faces("%Plane").size()
        assert n_planar >= 9, f"Expected at least 9 planar faces, got {n_planar}"
    
        # Check the peak heights are present in the bounding box
        assert bb.ymax >= h_peak2 - TOL, f"Max height should be at least peak2 height {h_peak2}"
    
        print(f"Bounding box: X=[{bb.xmin:.4f}, {bb.xmax:.4f}], Y=[{bb.ymin:.4f}, {bb.ymax:.4f}], Z=[{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Planar faces: {n_planar}")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00671898/gpt_generated.stl')
