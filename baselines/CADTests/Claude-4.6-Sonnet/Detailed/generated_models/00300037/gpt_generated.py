import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        u_width = 0.75          # total width of U in X
        u_height = 0.199115     # total height of U in Y
        extrude_h = 0.165929    # extrusion height in Z
    
        sq_w = 0.126106         # rectangle width in X
        sq_h = 0.225664         # rectangle height in Y
    
        # Arm width matches sq_w; bottom bar = half of u_height
        arm_w = sq_w            # 0.126106
        bottom_bar = u_height * 0.5
        inner_h = u_height - bottom_bar   # height of inner cutout
        inner_w = u_width - 2 * arm_w    # width of inner cutout = 0.497788
    
        # U-shape centered at origin on XY plane
        # x: -0.375 to +0.375, y: -u_height/2 to +u_height/2
        x0 = -u_width / 2    # -0.375
        y0 = -u_height / 2   # -0.0995575
        x1 =  u_width / 2    #  0.375
        y1 =  u_height / 2   #  0.0995575
    
        # --- Step 1: Build U-shape by extruding full rect then cutting inner notch ---
        # Full rectangle extrusion
        u_shape = (
            cq.Workplane("XY")
            .rect(u_width, u_height)
            .extrude(extrude_h)
        )
    
        # Inner notch: centered in X, at the top of the U
        # Notch spans from ix0 to ix1 in X, from iy0 to y1 in Y
        ix0 = x0 + arm_w   # -0.375 + 0.126106 = -0.248894
        ix1 = x1 - arm_w   #  0.375 - 0.126106 =  0.248894
        iy0 = y0 + bottom_bar  # bottom of notch
    
        notch_cx = 0.0
        notch_cy = (iy0 + y1) / 2.0   # center Y of notch
        notch_w = inner_w
        notch_h = inner_h
    
        notch = (
            cq.Workplane("XY")
            .center(notch_cx, notch_cy)
            .rect(notch_w, notch_h)
            .extrude(extrude_h)
        )
    
        u_shape = u_shape.cut(notch)
    
        # --- Step 2: Two rectangles at bottom-left and bottom-right corners ---
        # slight overlap into the U arms
        overlap = 0.01
    
        # Left rectangle: right edge slightly inside the U's left arm
        # right edge at x0 + arm_w + overlap = -0.375 + 0.126106 + 0.01 = -0.238894
        # left edge at right_edge - sq_w = -0.238894 - 0.126106 = -0.365
        left_cx = x0 + arm_w + overlap - sq_w / 2
        left_cy = y0 + sq_h / 2   # bottom edge at y0
    
        # Right rectangle: mirror of left
        right_cx = x1 - arm_w - overlap + sq_w / 2
        right_cy = y0 + sq_h / 2
    
        left_sq = (
            cq.Workplane("XY")
            .center(left_cx, left_cy)
            .rect(sq_w, sq_h)
            .extrude(extrude_h)
        )
    
        right_sq = (
            cq.Workplane("XY")
            .center(right_cx, right_cy)
            .rect(sq_w, sq_h)
            .extrude(extrude_h)
        )
    
        # --- Step 3: Union all parts ---
        result = u_shape.union(left_sq).union(right_sq)
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # Print actual values for diagnosis
        print(f"Actual bbox: xmin={bb.xmin:.4f}, xmax={bb.xmax:.4f}, "
              f"ymin={bb.ymin:.4f}, ymax={bb.ymax:.4f}, "
              f"zmin={bb.zmin:.4f}, zmax={bb.zmax:.4f}")
    
        # Left square left edge:  left_cx - sq_w/2
        # Right square right edge: right_cx + sq_w/2
        left_sq_xmin = left_cx - sq_w / 2
        right_sq_xmax = right_cx + sq_w / 2
    
        print(f"U x0={x0:.4f}, x1={x1:.4f}")
        print(f"Left sq xmin={left_sq_xmin:.4f}, right sq xmax={right_sq_xmax:.4f}")
    
        # xmin: U extends to x0=-0.375, left square to left_sq_xmin=-0.365
        # So xmin should be x0 = -0.375
        expected_xmin = x0
        # xmax: U extends to x1=0.375, right square to right_sq_xmax=0.365
        # So xmax should be x1 = 0.375
        expected_xmax = x1
        assert abs(bb.xmin - expected_xmin) < TOL, \
            f"xmin: expected {expected_xmin:.4f}, got {bb.xmin:.4f}"
        assert abs(bb.xmax - expected_xmax) < TOL, \
            f"xmax: expected {expected_xmax:.4f}, got {bb.xmax:.4f}"
        assert abs(bb.xlen - u_width) < TOL, \
            f"xlen: expected {u_width:.4f}, got {bb.xlen:.4f}"
    
        # ymin: both U and squares start at y0
        # ymax: squares extend to y0 + sq_h (taller than U's y1)
        expected_ymin = y0
        expected_ymax = y0 + sq_h
        assert abs(bb.ymin - expected_ymin) < TOL, \
            f"ymin: expected {expected_ymin:.4f}, got {bb.ymin:.4f}"
        assert abs(bb.ymax - expected_ymax) < TOL, \
            f"ymax: expected {expected_ymax:.4f}, got {bb.ymax:.4f}"
    
        # Z: 0 to extrude_h
        assert abs(bb.zmin - 0.0) < TOL, \
            f"zmin: expected 0.0, got {bb.zmin:.4f}"
        assert abs(bb.zmax - extrude_h) < TOL, \
            f"zmax: expected {extrude_h:.4f}, got {bb.zmax:.4f}"
        assert abs(bb.zlen - extrude_h) < TOL, \
            f"Z length: expected {extrude_h:.4f}, got {bb.zlen:.4f}"
    
        # Volume check
        u_vol = (u_width * u_height - inner_w * inner_h) * extrude_h
        sq_vol = sq_w * sq_h * extrude_h
        total_vol = result.val().Volume()
        assert total_vol > 0, f"Volume should be positive, got {total_vol}"
        assert total_vol >= u_vol * 0.9, \
            f"Volume too small: {total_vol:.6f} vs U_vol {u_vol:.6f}"
        assert total_vol <= (u_vol + 2 * sq_vol) * 1.1, \
            f"Volume too large: {total_vol:.6f}"
    
        # Single solid
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        print(f"Volume: {total_vol:.6f}")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00300037/gpt_generated.stl')
