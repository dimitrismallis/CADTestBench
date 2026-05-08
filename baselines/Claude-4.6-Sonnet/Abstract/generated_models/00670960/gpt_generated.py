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
        rect_len = 60.0      # rectangle length along X
        rect_wid = 50.0      # rectangle width along Y (shorter side)
        extrude_h = 3.0      # extrusion height
    
        # Trapezium parameters
        trap_base = (2.0 / 3.0) * rect_wid   # ~33.33mm base
        trap_side = trap_base / 10.0          # ~3.33mm angular sides
        trap_angle_deg = 45.0
        trap_angle_rad = math.radians(trap_angle_deg)
        trap_height = trap_side * math.sin(trap_angle_rad)   # ~2.357mm
        trap_top = trap_base - 2 * trap_side * math.cos(trap_angle_rad)  # ~28.66mm
    
        # Trapezium center offset: marginally to the right of center of shorter edge
        # The shorter edge is at X = +rect_len/2, running along Y from -rect_wid/2 to +rect_wid/2
        # Center of shorter edge is at Y=0; "marginally to the right" -> slight +Y offset
        trap_center_y = 2.0   # 2mm offset to the right
    
        # Trapezium base runs along Y at X = rect_len/2
        # Base: from (rect_len/2, trap_center_y - trap_base/2) to (rect_len/2, trap_center_y + trap_base/2)
        # Top: from (rect_len/2 + trap_height, trap_center_y - trap_top/2) to (rect_len/2 + trap_height, trap_center_y + trap_top/2)
    
        rx = rect_len / 2.0   # 30
        ry = rect_wid / 2.0   # 25
    
        # Trapezium base endpoints (at X = rx)
        tb_y1 = trap_center_y - trap_base / 2.0   # bottom of base
        tb_y2 = trap_center_y + trap_base / 2.0   # top of base
    
        # Trapezium top endpoints (at X = rx + trap_height)
        tt_y1 = trap_center_y - trap_top / 2.0    # bottom of top
        tt_y2 = trap_center_y + trap_top / 2.0    # top of top
    
        # --- Step 1: Build the combined outline as a closed wire ---
        # We trace the outline of the combined shape (rectangle + trapezium on right edge)
        # Starting from bottom-left corner, going clockwise:
        # Bottom-left -> Bottom-right (along bottom edge of rectangle)
        # Then up the right edge to where trapezium base starts (tb_y1)
        # Then into the trapezium (bottom angular side to top-right, across top, back bottom angular side)
        # Then continue up the right edge to top-right corner
        # Then across top edge to top-left
        # Then down left edge back to start
    
        # Points (all in 2D, XY plane):
        # Rectangle corners
        p_bl = (-rx, -ry)          # bottom-left
        p_br = (rx, -ry)           # bottom-right
        p_tr = (rx, ry)            # top-right
        p_tl = (-rx, ry)           # top-left
    
        # Trapezium points
        p_tb1 = (rx, tb_y1)        # base bottom
        p_tb2 = (rx, tb_y2)        # base top
        p_tt1 = (rx + trap_height, tt_y1)   # top bottom
        p_tt2 = (rx + trap_height, tt_y2)   # top top
    
        # Build the closed wire by tracing the outline
        # Order: p_bl -> p_br -> p_tb1 -> p_tt1 -> p_tt2 -> p_tb2 -> p_tr -> p_tl -> p_bl
        result = (
            cq.Workplane("XY")
            .moveTo(*p_bl)
            .lineTo(*p_br)
            .lineTo(*p_tb1)
            .lineTo(*p_tt1)
            .lineTo(*p_tt2)
            .lineTo(*p_tb2)
            .lineTo(*p_tr)
            .lineTo(*p_tl)
            .close()
            .extrude(extrude_h)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # X extent: from -rx to rx + trap_height
        expected_xlen = rect_len + trap_height
        assert abs(bb.xlen - expected_xlen) < TOL, f"X length: expected {expected_xlen:.3f}, got {bb.xlen:.3f}"
    
        # Y extent: from -ry to ry (rectangle dominates, trapezium center is only +2mm offset)
        expected_ylen = rect_wid
        assert abs(bb.ylen - expected_ylen) < TOL, f"Y length: expected {expected_ylen:.3f}, got {bb.ylen:.3f}"
    
        # Z extent: extrusion height
        assert abs(bb.zlen - extrude_h) < TOL, f"Z length: expected {extrude_h}, got {bb.zlen:.3f}"
    
        # Volume: (rectangle area + trapezium area) * extrude_h
        rect_area = rect_len * rect_wid
        trap_area = 0.5 * (trap_base + trap_top) * trap_height
        expected_vol = (rect_area + trap_area) * extrude_h
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.3f}, got {actual_vol:.3f}"
    
        # Face count: the extruded shape has 2 flat faces (top/bottom) + side faces
        # The outline has 8 segments -> 8 side faces + 2 end faces = 10 total
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # Check the shape is planar on top and bottom
        assert result.faces(">Z").size() == 1, "Should have exactly 1 top face"
        assert result.faces("<Z").size() == 1, "Should have exactly 1 bottom face"
    
        # Check bounding box X min/max
        assert abs(bb.xmin - (-rx)) < TOL, f"X min: expected {-rx}, got {bb.xmin:.3f}"
        assert abs(bb.xmax - (rx + trap_height)) < TOL, f"X max: expected {rx + trap_height:.3f}, got {bb.xmax:.3f}"
    
        # Check bounding box Y min/max
        assert abs(bb.ymin - (-ry)) < TOL, f"Y min: expected {-ry}, got {bb.ymin:.3f}"
        assert abs(bb.ymax - ry) < TOL, f"Y max: expected {ry}, got {bb.ymax:.3f}"
    
        # Check bounding box Z
        assert abs(bb.zmin - 0.0) < TOL, f"Z min: expected 0, got {bb.zmin:.3f}"
        assert abs(bb.zmax - extrude_h) < TOL, f"Z max: expected {extrude_h}, got {bb.zmax:.3f}"
    
        # Verify the trapezium protrudes: a point inside the trapezium region should be inside the solid
        trap_mid_x = rx + trap_height / 2.0
        trap_mid_y = trap_center_y
        trap_mid_z = extrude_h / 2.0
        assert result.val().isInside((trap_mid_x, trap_mid_y, trap_mid_z)), \
            "Point inside trapezium region should be inside the solid"
    
        # Verify a point outside the trapezium (but at same X) is outside the solid
        outside_y = trap_center_y - trap_base  # well below the trapezium base
        assert not result.val().isInside((trap_mid_x, outside_y, trap_mid_z)), \
            "Point outside trapezium should not be inside the solid"
    
        print(f"Trapezium base: {trap_base:.3f} mm")
        print(f"Trapezium side: {trap_side:.3f} mm")
        print(f"Trapezium height: {trap_height:.3f} mm")
        print(f"Trapezium top: {trap_top:.3f} mm")
        print(f"Trapezium center Y offset: {trap_center_y} mm")
        print(f"Bounding box: X={bb.xlen:.3f}, Y={bb.ylen:.3f}, Z={bb.zlen:.3f}")
        print(f"Volume: {actual_vol:.3f} mm³ (expected {expected_vol:.3f})")
        print(f"Face count: {face_count}")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00670960/gpt_generated.stl')
