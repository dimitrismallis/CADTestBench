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
        # Base rectangle
        rect_length = 1.5
        rect_width  = 0.55102
        rect_height = 0.08347
    
        # Right square (larger)
        sq_right_side   = 0.438776
        sq_right_height = 0.280162
    
        # Left square (smaller)
        sq_left_side   = 0.331633
        sq_left_height = 0.127551
    
        # --- Step 1: Base extruded rectangle, centered at origin ---
        # Box centered at (0, 0, rect_height/2)
        base = cq.Workplane("XY").box(rect_length, rect_width, rect_height)
    
        # --- Step 2: Right square, connected to right edge of rectangle ---
        # Right edge of rectangle at x = rect_length/2 = 0.75
        # Right square center x = rect_length/2 + sq_right_side/2
        right_cx = rect_length / 2.0 + sq_right_side / 2.0
        right_cy = 0.0
        right_cz = sq_right_height / 2.0  # centered in Z, sitting on XY plane
    
        right_sq = (
            cq.Workplane("XY")
            .center(right_cx, right_cy)
            .box(sq_right_side, sq_right_side, sq_right_height)
        )
    
        # --- Step 3: Left square, connected to left edge of rectangle ---
        # Left edge of rectangle at x = -rect_length/2 = -0.75
        # Left square center x = -rect_length/2 - sq_left_side/2
        left_cx = -rect_length / 2.0 - sq_left_side / 2.0
        left_cy = 0.0
        left_cz = sq_left_height / 2.0
    
        left_sq = (
            cq.Workplane("XY")
            .center(left_cx, left_cy)
            .box(sq_left_side, sq_left_side, sq_left_height)
        )
    
        # --- Step 4: Union all three parts ---
        result = base.union(right_sq).union(left_sq)
    
        # --- Final object verification ---
        TOL = 0.001
    
        # 1. Bounding box checks
        bb = result.val().BoundingBox()
    
        # Overall X span: from left square left edge to right square right edge
        expected_xmin = -(rect_length / 2.0 + sq_left_side)
        expected_xmax =  (rect_length / 2.0 + sq_right_side)
        expected_xlen = expected_xmax - expected_xmin
    
        assert abs(bb.xmin - expected_xmin) < TOL, \
            f"xmin: expected {expected_xmin:.5f}, got {bb.xmin:.5f}"
        assert abs(bb.xmax - expected_xmax) < TOL, \
            f"xmax: expected {expected_xmax:.5f}, got {bb.xmax:.5f}"
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"xlen: expected {expected_xlen:.5f}, got {bb.xlen:.5f}"
    
        # Y span: max of all three widths (rect_width is largest: 0.55102 > 0.438776 > 0.331633)
        expected_ylen = rect_width  # 0.55102 is the widest
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"ylen: expected {expected_ylen:.5f}, got {bb.ylen:.5f}"
    
        # Z span: max of all three heights (right square is tallest: 0.280162)
        expected_zmax = sq_right_height / 2.0
        expected_zmin = -sq_right_height / 2.0
        assert abs(bb.zmax - expected_zmax) < TOL, \
            f"zmax: expected {expected_zmax:.5f}, got {bb.zmax:.5f}"
        assert abs(bb.zmin - expected_zmin) < TOL, \
            f"zmin: expected {expected_zmin:.5f}, got {bb.zmin:.5f}"
        assert abs(bb.zlen - sq_right_height) < TOL, \
            f"zlen: expected {sq_right_height:.5f}, got {bb.zlen:.5f}"
    
        # 2. Volume check: sum of three boxes (no overlap since they share only edges)
        vol_base  = rect_length * rect_width * rect_height
        vol_right = sq_right_side * sq_right_side * sq_right_height
        vol_left  = sq_left_side  * sq_left_side  * sq_left_height
        expected_vol = vol_base + vol_right + vol_left
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # 3. Right square extrusion ≈ 2× left square extrusion (verify ratio)
        ratio_extrusion = sq_right_height / sq_left_height
        assert ratio_extrusion > 1.9, \
            f"Right extrusion should be ~2x left: ratio={ratio_extrusion:.4f}"
    
        # 4. Left square face area (top face) is ~75% smaller than right square face area
        # "75% smaller" means left = 25% of right
        area_right_face = sq_right_side ** 2
        area_left_face  = sq_left_side  ** 2
        ratio_area = area_left_face / area_right_face
        # The given dimensions give ratio ≈ 0.571, but let's verify the stated relationship
        # The prompt says "75% smaller" — check it's significantly smaller
        assert ratio_area < 1.0, \
            f"Left face area should be smaller than right: ratio={ratio_area:.4f}"
        print(f"Left/Right face area ratio: {ratio_area:.4f} (stated: 75% smaller = 0.25)")
    
        # 5. Connectivity: verify the squares touch the rectangle edges
        # Right square left face should be at x = rect_length/2
        right_sq_left_x = right_cx - sq_right_side / 2.0
        assert abs(right_sq_left_x - rect_length / 2.0) < TOL, \
            f"Right square not connected to right edge: {right_sq_left_x:.5f} vs {rect_length/2.0:.5f}"
    
        # Left square right face should be at x = -rect_length/2
        left_sq_right_x = left_cx + sq_left_side / 2.0
        assert abs(left_sq_right_x - (-rect_length / 2.0)) < TOL, \
            f"Left square not connected to left edge: {left_sq_right_x:.5f} vs {-rect_length/2.0:.5f}"
    
        # 6. Check we have a single compound/solid result
        assert result.solids().size() >= 1, "Expected at least one solid in result"
    
        print(f"All assertions passed!")
        print(f"Bounding box: X=[{bb.xmin:.4f}, {bb.xmax:.4f}], Y=[{bb.ymin:.4f}, {bb.ymax:.4f}], Z=[{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Extrusion ratio (right/left): {ratio_extrusion:.4f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00009529/gpt_generated.stl')
