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
        diameter = 0.374906
        height = 0.1875
        radius = diameter / 2
    
        # Circle center
        cx = diameter / 2                           # 0.187453
        cy = diameter * 2 - 0.187124               # 0.562688
    
        # Polygon points
        p0 = (0.0, 0.0)
        p1 = (0.0, diameter)                        # (0, 0.374906)
        p2x = (diameter * 0.7) + 0.01883 - 0.0001  # ~0.280533
        p2 = (p2x, diameter)
    
        # The circle bottom is at cy - radius = 0.562688 - 0.187453 = 0.375235
        # The polygon top is at y = diameter = 0.374906
        # Gap = 0.375235 - 0.374906 = 0.000329 — they don't overlap!
        # Fix: extend polygon top edge up to cy so it overlaps the circle
    
        # We'll build the combined shape by extending the polygon to overlap the circle,
        # then union them. Extend p1 and p2 y-coordinate to cy to guarantee overlap.
        p1_ext = (0.0, cy)
        p2_ext = (p2x, cy)
    
        # --- Step 1: Build the polygon solid (extended to overlap circle) ---
        poly_solid = (
            cq.Workplane("XY")
            .moveTo(p0[0], p0[1])
            .lineTo(p1_ext[0], p1_ext[1])
            .lineTo(p2_ext[0], p2_ext[1])
            .close()
            .extrude(height)
        )
    
        # --- Step 2: Build the circle solid ---
        circle_solid = (
            cq.Workplane("XY")
            .moveTo(cx, cy)
            .circle(radius)
            .extrude(height)
        )
    
        # --- Step 3: Union the two overlapping solids ---
        result = poly_solid.union(circle_solid)
    
        # --- Step 4: Translate to center vertically ---
        result = result.translate((0, 0, -height / 2))
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # Z should span from -height/2 to +height/2
        assert abs(bb.zlen - height) < TOL, \
            f"Z height: expected {height}, got {bb.zlen}"
        assert abs(bb.zmin - (-height / 2)) < TOL, \
            f"Z min: expected {-height/2}, got {bb.zmin}"
        assert abs(bb.zmax - (height / 2)) < TOL, \
            f"Z max: expected {height/2}, got {bb.zmax}"
    
        # X bounding box: from 0 to diameter (cx + radius = diameter/2 + diameter/2)
        expected_xmin = 0.0
        expected_xmax = cx + radius  # = diameter = 0.374906
        assert abs(bb.xmin - expected_xmin) < TOL, \
            f"X min: expected {expected_xmin}, got {bb.xmin}"
        assert abs(bb.xmax - expected_xmax) < TOL, \
            f"X max: expected {expected_xmax}, got {bb.xmax}"
    
        # Y bounding box: from 0 to cy + radius
        expected_ymin = 0.0
        expected_ymax = cy + radius  # 0.562688 + 0.187453 = 0.750141
        assert abs(bb.ymin - expected_ymin) < TOL, \
            f"Y min: expected {expected_ymin}, got {bb.ymin}"
        assert abs(bb.ymax - expected_ymax) < TOL, \
            f"Y max: expected {expected_ymax}, got {bb.ymax}"
    
        # Volume check: combined area * height
        # Extended triangle area = 0.5 * p2x * cy
        tri_area = 0.5 * p2x * cy
        circle_area = math.pi * radius ** 2
        vol = result.val().Volume()
        # Union volume <= sum of both, >= max of both
        max_vol = (tri_area + circle_area) * height
        min_vol = max(tri_area, circle_area) * height
        assert vol > min_vol * 0.9, \
            f"Volume too small: {vol} < {min_vol * 0.9}"
        assert vol < max_vol * 1.1, \
            f"Volume too large: {vol} > {max_vol * 1.1}"
    
        # Check it's a single solid
        solids = result.solids().size()
        assert solids == 1, f"Expected 1 solid, got {solids}"
    
        # Check the shape contains the circle center point (at z=0)
        center_point = cq.Vector(cx, cy, 0)
        assert result.val().isInside(center_point), \
            f"Circle center should be inside the shape"
    
        # Check the polygon centroid is inside
        poly_centroid = cq.Vector(
            (p0[0] + p1_ext[0] + p2_ext[0]) / 3,
            (p0[1] + p1_ext[1] + p2_ext[1]) / 3,
            0
        )
        assert result.val().isInside(poly_centroid), \
            f"Polygon centroid should be inside the shape"
    
        print(f"Bounding box: X=[{bb.xmin:.4f}, {bb.xmax:.4f}], "
              f"Y=[{bb.ymin:.4f}, {bb.ymax:.4f}], Z=[{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"Volume: {vol:.6f}")
        print(f"Solids: {solids}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00857821/gpt_generated.stl')
