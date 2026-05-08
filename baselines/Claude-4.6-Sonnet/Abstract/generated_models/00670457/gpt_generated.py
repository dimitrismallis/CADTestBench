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
        rect_length = 60.0   # long dimension of rectangle
        rect_width  = 20.0   # short dimension of rectangle
        trap_height = 15.0   # height (horizontal extent) of trapezium
        trap_top    = 10.0   # top (shorter parallel side) of trapezium
        extrude_h   = 10.0   # extrusion depth
    
        # Half-widths for convenience
        hw = rect_width / 2.0       # 10.0
        trap_top_hw = trap_top / 2.0  # 5.0
    
        # --- Step 1: Build the combined 2D profile as a closed wire ---
        # The rectangle runs from x=0 to x=rect_length, centered on Y axis.
        # The trapezium attaches to the right short edge (x=rect_length),
        # base = rect_width (from y=-hw to y=+hw),
        # top = trap_top (from y=-trap_top_hw to y=+trap_top_hw),
        # apex at x = rect_length + trap_height.
    
        # Vertices of the combined profile (CCW when viewed from +Z):
        # 1. Bottom-left of rectangle
        # 2. Bottom-right of rectangle = bottom of trapezium base
        # 3. Bottom of trapezium top
        # 4. Top of trapezium top
        # 5. Top of trapezium base = top-right of rectangle
        # 6. Top-left of rectangle
    
        pts = [
            (0.0,                        -hw),           # 1
            (rect_length,                -hw),           # 2
            (rect_length + trap_height,  -trap_top_hw),  # 3
            (rect_length + trap_height,   trap_top_hw),  # 4
            (rect_length,                 hw),           # 5
            (0.0,                         hw),           # 6
        ]
    
        # Build the profile using lineTo and close()
        result = (
            cq.Workplane("XY")
            .moveTo(pts[0][0], pts[0][1])
            .lineTo(pts[1][0], pts[1][1])
            .lineTo(pts[2][0], pts[2][1])
            .lineTo(pts[3][0], pts[3][1])
            .lineTo(pts[4][0], pts[4][1])
            .lineTo(pts[5][0], pts[5][1])
            .close()
            .extrude(extrude_h)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        total_length = rect_length + trap_height   # 75.0
        assert abs(bb.xlen - total_length) < TOL, \
            f"X length: expected {total_length}, got {bb.xlen}"
        assert abs(bb.ylen - rect_width) < TOL, \
            f"Y length: expected {rect_width}, got {bb.ylen}"
        assert abs(bb.zlen - extrude_h) < TOL, \
            f"Z length: expected {extrude_h}, got {bb.zlen}"
    
        # Volume check:
        # Rectangle area = rect_length * rect_width = 60 * 20 = 1200
        # Trapezium area = 0.5 * (base + top) * height = 0.5 * (20 + 10) * 15 = 225
        # Total 2D area = 1425
        # Volume = 1425 * extrude_h = 14250
        rect_area = rect_length * rect_width
        trap_area = 0.5 * (rect_width + trap_top) * trap_height
        expected_vol = (rect_area + trap_area) * extrude_h
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count: 
        # Bottom face (1), Top face (1), 
        # Left face (1), Right-top face (1), Right-bottom face (1),
        # Trapezium top-slant (1), Trapezium bottom-slant (1)
        # = 8 faces total (6 sides + top + bottom)
        face_count = result.faces().size()
        assert face_count == 8, \
            f"Face count: expected 8, got {face_count}"
    
        # All faces should be planar
        planar_count = result.faces("%Plane").size()
        assert planar_count == 8, \
            f"Planar face count: expected 8, got {planar_count}"
    
        # Check the solid is a single solid
        solid_count = result.solids().size()
        assert solid_count == 1, \
            f"Solid count: expected 1, got {solid_count}"
    
        # Check bounding box origin (xmin should be 0, ymin should be -hw)
        assert abs(bb.xmin - 0.0) < TOL, \
            f"xmin: expected 0.0, got {bb.xmin}"
        assert abs(bb.ymin - (-hw)) < TOL, \
            f"ymin: expected {-hw}, got {bb.ymin}"
        assert abs(bb.zmin - 0.0) < TOL, \
            f"zmin: expected 0.0, got {bb.zmin}"
    
        # Check center of mass is shifted toward the trapezium side (x > rect_length/2)
        com = cq.Shape.centerOfMass(result.val())
        assert com.x > rect_length / 2.0, \
            f"Center of mass X should be > {rect_length/2.0}, got {com.x}"
        assert abs(com.y) < TOL, \
            f"Center of mass Y should be ~0 (symmetric), got {com.y}"
    
        # Check a point inside the rectangle region is inside the solid
        assert result.val().isInside((30.0, 0.0, 5.0)), \
            "Point (30, 0, 5) should be inside the solid (rectangle region)"
    
        # Check a point inside the trapezium region is inside the solid
        assert result.val().isInside((65.0, 0.0, 5.0)), \
            "Point (65, 0, 5) should be inside the solid (trapezium region)"
    
        # Check a point outside the trapezium (beyond the tip) is outside
        assert not result.val().isInside((80.0, 0.0, 5.0)), \
            "Point (80, 0, 5) should be outside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00670457/gpt_generated.stl')
