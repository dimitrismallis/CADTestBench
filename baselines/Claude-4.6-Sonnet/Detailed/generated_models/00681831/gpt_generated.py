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
        diameter = 0.955953
        radius = diameter / 2.0          # 0.477977
        width = 0.295686
        base_length = 0.163062
        top_length = 0.163062            # same as base → rectangle
        trap_height = diameter - 0.698688  # 0.955953 - 0.698688 = 0.257265
    
        # --- Step 1: Build the 2D profile using Sketch API ---
        # Circle with a rectangular notch cut from the top
        # The notch (trapezoid) is centered at x=0, top edge at y=radius,
        # bottom edge at y = radius - trap_height
        notch_top_y    = radius                        # 0.477977
        notch_bottom_y = radius - trap_height          # 0.477977 - 0.257265 = 0.220712
        notch_center_y = (notch_top_y + notch_bottom_y) / 2.0  # 0.349344
        notch_height   = trap_height                   # 0.257265
        notch_width    = base_length                   # 0.163062 (same top and bottom)
    
        # Use Sketch: start with circle, subtract rectangle at top
        sketch = (
            cq.Sketch()
            .circle(radius)
            .reset()
            .push([(0, notch_center_y)])
            .rect(notch_width, notch_height, mode="s")
        )
    
        # --- Step 2: Extrude the sketch along Z by width ---
        result = (
            cq.Workplane("XY")
            .placeSketch(sketch)
            .extrude(width)
        )
    
        # --- Step 3: Translate to final position ---
        # Translate by (0, width/2, -0.272116)
        tx, ty, tz = 0.0, width / 2.0, -0.272116
        result = result.translate((tx, ty, tz))
    
        # --- Final object verification ---
        TOL = 0.01
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box X: should span roughly -radius to +radius = diameter
        assert abs(bb.xlen - diameter) < TOL, \
            f"X extent: expected ~{diameter}, got {bb.xlen}"
    
        # Bounding box Z (after translation): extrusion was along Z for width,
        # then translated by tz = -0.272116
        # Z range: tz to tz + width
        expected_zmin = tz
        expected_zmax = tz + width
        assert abs(bb.zmin - expected_zmin) < TOL, \
            f"Z min: expected ~{expected_zmin}, got {bb.zmin}"
        assert abs(bb.zmax - expected_zmax) < TOL, \
            f"Z max: expected ~{expected_zmax}, got {bb.zmax}"
        assert abs(bb.zlen - width) < TOL, \
            f"Z extent (width): expected ~{width}, got {bb.zlen}"
    
        # Y bounding box: circle goes from -radius to +radius, then translated by ty=width/2
        expected_ymin = -radius + ty
        expected_ymax = radius + ty
        assert abs(bb.ymin - expected_ymin) < TOL, \
            f"Y min: expected ~{expected_ymin}, got {bb.ymin}"
        assert abs(bb.ymax - expected_ymax) < TOL, \
            f"Y max: expected ~{expected_ymax}, got {bb.ymax}"
    
        # Volume: circle area minus notch area, times width
        circle_area = math.pi * radius ** 2
        notch_area   = notch_width * notch_height
        expected_vol = (circle_area - notch_area) * width
        actual_vol   = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Should have cylindrical faces (from the circle extrusion)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # Should have planar faces (top, bottom, notch walls)
        plane_faces = result.faces("%Plane").size()
        assert plane_faces >= 4, f"Expected at least 4 planar faces, got {plane_faces}"
    
        # Center of mass should be near x=0 (symmetric about YZ plane)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"Center of mass X: expected ~0, got {com.x}"
    
        print(f"All assertions passed!")
        print(f"  Bounding box: x={bb.xlen:.4f}, y={bb.ylen:.4f}, z={bb.zlen:.4f}")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"  Cylindrical faces: {cyl_faces}, Planar faces: {plane_faces}")
        print(f"  Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00681831/gpt_generated.stl')
