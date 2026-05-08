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
        W = 20.0          # rectangle width
        rect_h = W / 20   # = 1.0  (thin rectangle height)
        sq1_side = W / 2  # = 10.0 (first square side)
        sq2_side = sq1_side * 0.9  # = 9.0 (second square, slightly smaller)
        depth = 20 * W    # = 400.0 (extrusion depth)
    
        # --- Step 1: Define profile vertices ---
        # Rectangle: x=[0, W], y=[0, rect_h]
        # Square 1:  x=[W/2, W], y=[rect_h, rect_h + sq1_side]
        #            bottom-right = (W, rect_h) = top-right of rectangle ✓
        #            bottom-left  = (W/2, rect_h) on vertical line x=W/2 (center of rect) ✓
        # Square 2:  x=[W - sq2_side, W], y=[rect_h + sq1_side, rect_h + sq1_side + sq2_side]
        #            bottom-right = (W, rect_h + sq1_side) = top-right of Square 1 ✓
    
        x0 = 0.0
        x_center = W / 2          # = 10.0
        x_sq2_left = W - sq2_side  # = 11.0
        x_right = W               # = 20.0
    
        y0 = 0.0
        y1 = rect_h                        # = 1.0  (top of rectangle)
        y2 = rect_h + sq1_side             # = 11.0 (top of square 1)
        y3 = rect_h + sq1_side + sq2_side  # = 20.0 (top of square 2)
    
        # Closed polygon vertices (counterclockwise)
        pts = [
            (x0,       y0),   # bottom-left of rectangle
            (x_right,  y0),   # bottom-right of rectangle
            (x_right,  y3),   # top-right of square 2
            (x_sq2_left, y3), # top-left of square 2
            (x_sq2_left, y2), # bottom-left of square 2 = top-left of square 1 area
            (x_center, y2),   # top-left of square 1
            (x_center, y1),   # bottom-left of square 1 = top-left of rectangle area
            (x0,       y1),   # top-left of rectangle
        ]
    
        # --- Step 2: Build the 2D profile as a closed wire ---
        profile = (
            cq.Workplane("XY")
            .moveTo(pts[0][0], pts[0][1])
            .lineTo(pts[1][0], pts[1][1])
            .lineTo(pts[2][0], pts[2][1])
            .lineTo(pts[3][0], pts[3][1])
            .lineTo(pts[4][0], pts[4][1])
            .lineTo(pts[5][0], pts[5][1])
            .lineTo(pts[6][0], pts[6][1])
            .lineTo(pts[7][0], pts[7][1])
            .close()
        )
    
        # --- Step 3: Extrude the profile ---
        result = profile.extrude(depth)
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - W) < TOL, f"X extent: expected {W}, got {bb.xlen}"
        assert abs(bb.ylen - y3) < TOL, f"Y extent: expected {y3}, got {bb.ylen}"
        assert abs(bb.zlen - depth) < TOL, f"Z extent (depth): expected {depth}, got {bb.zlen}"
    
        # Bounding box origin checks
        assert abs(bb.xmin - 0.0) < TOL, f"xmin: expected 0, got {bb.xmin}"
        assert abs(bb.ymin - 0.0) < TOL, f"ymin: expected 0, got {bb.ymin}"
    
        # Volume check
        # Profile area = rectangle area + square1 area + square2 area
        rect_area  = W * rect_h                  # 20 * 1 = 20
        sq1_area   = sq1_side * sq1_side         # 10 * 10 = 100
        sq2_area   = sq2_side * sq2_side         # 9 * 9 = 81
        profile_area = rect_area + sq1_area + sq2_area  # 201
        expected_vol = profile_area * depth      # 201 * 400 = 80400
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol}, got {actual_vol}"
    
        # Face count: extruded polygon with 8 edges → 8 side faces + 2 end faces = 10
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # Check planar faces only (all faces should be planar for this shape)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 10, f"Planar face count: expected 10, got {planar_count}"
    
        # Check that the shape is a single solid
        solid_count = result.solids().size()
        assert solid_count == 1, f"Solid count: expected 1, got {solid_count}"
    
        # Verify key geometric points are inside the solid
        solid = result.val()
        # Center of rectangle region (extruded midway)
        assert solid.isInside((W/2, rect_h/2, depth/2)), \
            "Center of rectangle region should be inside solid"
        # Center of square 1 region
        assert solid.isInside((W*3/4, rect_h + sq1_side/2, depth/2)), \
            "Center of square 1 region should be inside solid"
        # Center of square 2 region
        assert solid.isInside(((x_sq2_left + x_right)/2, y2 + sq2_side/2, depth/2)), \
            "Center of square 2 region should be inside solid"
        # Point outside (left of square 1, above rectangle)
        assert not solid.isInside((W/4, rect_h + sq1_side/2, depth/2)), \
            "Left of square 1 should be outside solid"
        # Point outside (left of square 2, above square 1)
        assert not solid.isInside((W/4, y2 + sq2_side/2, depth/2)), \
            "Left of square 2 should be outside solid"
    
        print(f"All assertions passed!")
        print(f"  W={W}, rect_h={rect_h}, sq1_side={sq1_side}, sq2_side={sq2_side}, depth={depth}")
        print(f"  Bounding box: {bb.xlen} x {bb.ylen} x {bb.zlen}")
        print(f"  Volume: {actual_vol:.1f} (expected {expected_vol:.1f})")
        print(f"  Faces: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00997040/gpt_generated.stl')
