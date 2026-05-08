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
        bottom_len = 0.628103
        top_len    = 0.240157
        height     = 0.722001
        top_shift  = 0.009237   # top edge center shifted right from bottom center
        extrude_h  = 0.011084
        translate_x = -0.018474  # final translation left
    
        # --- Step 1: Compute trapezoid vertices in XY plane ---
        # Bottom edge centered at x=0
        bx_left  = -bottom_len / 2.0
        bx_right =  bottom_len / 2.0
        by       = 0.0
    
        # Top edge center shifted right by top_shift
        top_cx   = top_shift
        tx_left  = top_cx - top_len / 2.0
        tx_right = top_cx + top_len / 2.0
        ty       = height
    
        # Vertices in order (CCW): bottom-left, bottom-right, top-right, top-left
        v0 = (bx_left,  by)
        v1 = (bx_right, by)
        v2 = (tx_right, ty)
        v3 = (tx_left,  ty)
    
        # --- Step 2: Build the trapezoid sketch and extrude ---
        result = (
            cq.Workplane("XY")
            .moveTo(v0[0], v0[1])
            .lineTo(v1[0], v1[1])
            .lineTo(v2[0], v2[1])
            .lineTo(v3[0], v3[1])
            .close()
            .extrude(extrude_h)
        )
    
        # --- Step 3: Translate the extruded shape left by 0.018474 ---
        result = result.translate((translate_x, 0, 0))
    
        # --- Final object verification ---
        TOL = 1e-4
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # After translation, X bounds shift by translate_x
        expected_xmin = bx_left  + translate_x
        expected_xmax = bx_right + translate_x
        expected_ymin = 0.0
        expected_ymax = height
        expected_zmin = 0.0
        expected_zmax = extrude_h
    
        assert abs(bb.xmin - expected_xmin) < TOL, f"xmin: expected {expected_xmin:.6f}, got {bb.xmin:.6f}"
        assert abs(bb.xmax - expected_xmax) < TOL, f"xmax: expected {expected_xmax:.6f}, got {bb.xmax:.6f}"
        assert abs(bb.xlen - bottom_len) < TOL, f"xlen: expected {bottom_len:.6f}, got {bb.xlen:.6f}"
        assert abs(bb.ymin - expected_ymin) < TOL, f"ymin: expected {expected_ymin:.6f}, got {bb.ymin:.6f}"
        assert abs(bb.ymax - expected_ymax) < TOL, f"ymax: expected {expected_ymax:.6f}, got {bb.ymax:.6f}"
        assert abs(bb.ylen - height) < TOL, f"ylen: expected {height:.6f}, got {bb.ylen:.6f}"
        assert abs(bb.zmin - expected_zmin) < TOL, f"zmin: expected {expected_zmin:.6f}, got {bb.zmin:.6f}"
        assert abs(bb.zmax - expected_zmax) < TOL, f"zmax: expected {expected_zmax:.6f}, got {bb.zmax:.6f}"
        assert abs(bb.zlen - extrude_h) < TOL, f"zlen: expected {extrude_h:.6f}, got {bb.zlen:.6f}"
    
        # Volume: trapezoid area * extrude_h
        # Trapezoid area = 0.5 * (bottom_len + top_len) * height
        trap_area = 0.5 * (bottom_len + top_len) * height
        expected_vol = trap_area * extrude_h
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: a prism from a quadrilateral has 6 faces (2 trapezoid + 4 rectangular sides)
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # Check base angle approximately 70 degrees
        # Left side vector: from v0 to v3 (after translation, same angle)
        dx_left = tx_left - bx_left   # horizontal run
        dy_left = ty - by              # vertical rise
        angle_left = math.degrees(math.atan2(dy_left, dx_left))
        # Base angle is measured from horizontal bottom edge to left leg
        # The left leg goes from bottom-left upward and to the right
        # base angle = atan(height / horizontal_run_of_left_leg)
        left_leg_run = tx_left - bx_left  # this is negative if leg leans inward
        # Actually the base angle at bottom-left corner:
        # vector along bottom: (1, 0), vector along left leg: (tx_left - bx_left, height)
        left_leg_dx = tx_left - bx_left
        left_leg_dy = height
        base_angle_left = math.degrees(math.atan2(left_leg_dy, left_leg_dx))
        # For isosceles trapezoid with ~70 deg base angle, check it's near 70
        assert abs(base_angle_left - 70.0) < 5.0, \
            f"Left base angle: expected ~70 deg, got {base_angle_left:.2f} deg"
    
        # Verify top edge length (xlen of top edge region)
        # The top face (at y=height) should span top_len in X
        top_edges = result.edges(">Y")
        # Check that the top edge at max Y has length close to top_len
        top_edge_vals = top_edges.vals()
        # Find the horizontal top edge
        for e in top_edge_vals:
            ebb = e.BoundingBox()
            if abs(ebb.ymin - height) < TOL and abs(ebb.ymax - height) < TOL:
                if abs(ebb.zmin - ebb.zmax) < TOL:  # horizontal in XY
                    assert abs(ebb.xlen - top_len) < TOL, \
                        f"Top edge length: expected {top_len:.6f}, got {ebb.xlen:.6f}"
    
        print("All assertions passed!")
        print(f"  Bounding box: X=[{bb.xmin:.4f}, {bb.xmax:.4f}], Y=[{bb.ymin:.4f}, {bb.ymax:.4f}], Z=[{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"  Left base angle: {base_angle_left:.2f} deg")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00999141/gpt_generated.stl')
