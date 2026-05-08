import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Define star points ---
        points = [
            (0, 0.07722659),
            (0.01489577, 0.03904715),
            (0.07129721, 0.03904715),
            (0.01778815, 0.01070181),
            (0.05105054, -0.0378901),
            (0, -0.0083879),
            (-0.0539429, -0.03470857),
            (-0.02183747, 0.006074),
            (-0.07071871, 0.02429601),
            (-0.01865585, 0.036444),
            (0.0, 0.0772265),  # close back near start
        ]
    
        # --- Step 2: Build the star sketch as a closed polyline ---
        # Start at the first point, draw lines to each subsequent point, then close
        start = points[0]
        wp = cq.Workplane("XY").moveTo(start[0], start[1])
        for pt in points[1:]:
            wp = wp.lineTo(pt[0], pt[1])
        wp = wp.close()
    
        # --- Step 3: Extrude by the specified height ---
        extrude_height = 0.0634998086654784
        wp = wp.extrude(extrude_height)
    
        # --- Step 4: Scale by the specified factor ---
        scale_factor = 9.711714302145034
    
        # Use CadQuery's scale via the shell/solid transform
        # We use the Workplane's val() to get the solid, then apply scaling
        solid = wp.val()
        scaled_solid = solid.scale(scale_factor)
    
        # Wrap back into a Workplane
        result = cq.Workplane("XY").add(scaled_solid)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Get bounding box
        bb = result.val().BoundingBox()
    
        # Expected dimensions after scaling
        # X range: -0.07071871 to 0.07129721 → xlen = 0.14201592
        x_raw = 0.07129721 - (-0.07071871)  # = 0.14201592
        # Y range: -0.0378901 to 0.07722659 → ylen = 0.11511669
        y_raw = 0.07722659 - (-0.0378901)   # = 0.11511669
        # Z range: 0 to extrude_height
        z_raw = extrude_height
    
        expected_xlen = x_raw * scale_factor
        expected_ylen = y_raw * scale_factor
        expected_zlen = z_raw * scale_factor
    
        print(f"Bounding box: xlen={bb.xlen:.6f}, ylen={bb.ylen:.6f}, zlen={bb.zlen:.6f}")
        print(f"Expected:     xlen={expected_xlen:.6f}, ylen={expected_ylen:.6f}, zlen={expected_zlen:.6f}")
        print(f"Volume: {result.val().Volume():.6f}")
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen:.6f}, got {bb.xlen:.6f}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen:.6f}, got {bb.ylen:.6f}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen:.6f}, got {bb.zlen:.6f}"
    
        # Volume check: star area * height * scale^3
        # Approximate star area using shoelace formula
        pts_for_area = points[:-1]  # exclude closing duplicate
        n = len(pts_for_area)
        area = 0.0
        for i in range(n):
            x1, y1 = pts_for_area[i]
            x2, y2 = pts_for_area[(i + 1) % n]
            area += x1 * y2 - x2 * y1
        star_area = abs(area) / 2.0
        expected_vol = star_area * extrude_height * (scale_factor ** 3)
        actual_vol = result.val().Volume()
        print(f"Expected volume: {expected_vol:.6f}, Actual volume: {actual_vol:.6f}")
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.4f}, got {actual_vol:.4f}"
    
        # Check it has exactly 1 solid
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # Check the star has top and bottom planar faces
        planar_faces = result.faces("%Plane").size()
        print(f"Planar faces: {planar_faces}")
        # A 5-pointed star extruded: 2 star-shaped faces (top/bottom) + 10 side faces = 12 total
        assert planar_faces >= 12, \
            f"Expected at least 12 planar faces, got {planar_faces}"
    
        # Check center of mass is roughly at the centroid of the star scaled
        com = cq.Shape.centerOfMass(result.val())
        print(f"Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
        # Z center should be at half the scaled height
        expected_z_center = (expected_zlen) / 2.0
        assert abs(com.z - expected_z_center) < TOL, \
            f"Z center of mass: expected {expected_z_center:.4f}, got {com.z:.4f}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00681589/gpt_generated.stl')
