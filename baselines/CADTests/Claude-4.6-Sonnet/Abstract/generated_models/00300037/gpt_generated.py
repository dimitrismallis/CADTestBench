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
        H = 20          # extrusion height
        # U-shape outer dimensions (centered at origin)
        U_W = 60        # total width
        U_H = 40        # total height (Y direction)
        wall = 15       # wall thickness (arms and base)
        notch_w = 30    # notch width (inner gap)
        notch_h = 25    # notch height (from top)
    
        # Derived U-shape coordinates
        x_out_l = -U_W / 2   # -30
        x_out_r =  U_W / 2   #  30
        y_bot   = -U_H / 2   # -20
        y_top   =  U_H / 2   #  20
    
        # Notch (cut from top center)
        x_notch_l = -notch_w / 2  # -15
        x_notch_r =  notch_w / 2  #  15
        y_notch_bot = y_top - notch_h  # 20 - 25 = -5
    
        # Square parameters
        sq_size = 15
        overlap = 3  # how much the square overlaps the U corner
    
        # --- Step 1: Draw U-shaped profile as a closed wire ---
        # Trace the U outline starting from bottom-left outer corner
        u_shape = (
            cq.Workplane("XY")
            .moveTo(x_out_l, y_bot)           # bottom-left outer
            .lineTo(x_out_r, y_bot)           # bottom-right outer
            .lineTo(x_out_r, y_top)           # top-right outer
            .lineTo(x_notch_r, y_top)         # top-right notch start
            .lineTo(x_notch_r, y_notch_bot)   # notch bottom-right
            .lineTo(x_notch_l, y_notch_bot)   # notch bottom-left
            .lineTo(x_notch_l, y_top)         # top-left notch end
            .lineTo(x_out_l, y_top)           # top-left outer
            .close()
        )
    
        # --- Step 2: Extrude U-shape along Z ---
        u_solid = u_shape.extrude(H)
    
        # --- Step 3: Create left square ---
        # Bottom-left corner of U is at (x_out_l, y_bot) = (-30, -20)
        # Square overlaps by 'overlap' units into the U corner
        sq_cx_l = x_out_l - sq_size / 2 + overlap   # -30 - 7.5 + 3 = -34.5
        sq_cy   = y_bot   - sq_size / 2 + overlap   # -20 - 7.5 + 3 = -24.5
    
        left_sq = (
            cq.Workplane("XY")
            .moveTo(sq_cx_l, sq_cy)
            .rect(sq_size, sq_size)
            .extrude(H)
        )
    
        # --- Step 4: Create right square ---
        # Bottom-right corner of U is at (x_out_r, y_bot) = (30, -20)
        sq_cx_r = x_out_r + sq_size / 2 - overlap   # 30 + 7.5 - 3 = 34.5
    
        right_sq = (
            cq.Workplane("XY")
            .moveTo(sq_cx_r, sq_cy)
            .rect(sq_size, sq_size)
            .extrude(H)
        )
    
        # --- Step 5: Union all three parts ---
        result = u_solid.union(left_sq).union(right_sq)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X extent: from left square left edge to right square right edge
        # Left sq: center=-34.5, half=7.5 → left edge = -42
        # Right sq: center=34.5, half=7.5 → right edge = 42
        expected_xmin = -42.0
        expected_xmax =  42.0
        expected_xlen =  84.0
        assert abs(bb.xmin - expected_xmin) < TOL, \
            f"X min: expected {expected_xmin}, got {bb.xmin}"
        assert abs(bb.xmax - expected_xmax) < TOL, \
            f"X max: expected {expected_xmax}, got {bb.xmax}"
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen}, got {bb.xlen}"
    
        # Y extent: from square bottom to U top
        # Square bottom: sq_cy - sq_size/2 = -24.5 - 7.5 = -32
        # U top: y_top = 20
        expected_ymin = -32.0
        expected_ymax =  20.0
        expected_ylen =  52.0
        assert abs(bb.ymin - expected_ymin) < TOL, \
            f"Y min: expected {expected_ymin}, got {bb.ymin}"
        assert abs(bb.ymax - expected_ymax) < TOL, \
            f"Y max: expected {expected_ymax}, got {bb.ymax}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen}, got {bb.ylen}"
    
        # Z extent: extrusion height
        assert abs(bb.zmin - 0) < TOL, f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - H) < TOL, f"Z max: expected {H}, got {bb.zmax}"
        assert abs(bb.zlen - H) < TOL, f"Z length: expected {H}, got {bb.zlen}"
    
        # Volume check using inclusion-exclusion
        # Vol(U) = (outer_rect - notch) * H = (60*40 - 30*25) * 20 = 1650 * 20 = 33000
        # Vol(left_sq) = Vol(right_sq) = 15*15*20 = 4500
        # Overlap of left_sq with U:
        #   Left sq x: [-42, -27], U left arm x: [-30, -15] → x overlap: [-30, -27] = 3
        #   Left sq y: [-32, -17], U y: [-20, 20] → y overlap: [-20, -17] = 3
        #   Overlap area = 3*3 = 9, overlap vol = 9*20 = 180
        # By symmetry, same for right_sq
        # Total = 33000 + 4500 + 4500 - 180 - 180 = 41640
        # However, actual CadQuery volume may differ slightly due to numerical precision
        # Use a range check: volume should be between 41000 and 42000
        actual_vol = result.val().Volume()
        assert 41000 < actual_vol < 42000, \
            f"Volume out of expected range [41000, 42000]: got {actual_vol:.1f}"
    
        # More precise: volume should be close to 41640 within 2%
        expected_vol_approx = 41640.0
        assert abs(actual_vol - expected_vol_approx) / expected_vol_approx < 0.02, \
            f"Volume: expected ~{expected_vol_approx:.1f} (±2%), got {actual_vol:.1f}"
    
        # Check it's a single solid (union should produce one body)
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # Check top faces exist at Z=H
        top_faces = result.faces(">Z")
        assert top_faces.size() >= 1, "Should have at least one top face"
    
        # Check bottom faces exist at Z=0
        bot_faces = result.faces("<Z")
        assert bot_faces.size() >= 1, "Should have at least one bottom face"
    
        # Verify the notch (inner void) by checking a point inside the notch is NOT inside the solid
        notch_center_x = 0.0
        notch_center_y = (y_notch_bot + y_top) / 2  # (-5 + 20)/2 = 7.5
        notch_center_z = H / 2
        solid_shape = result.val()
        assert not solid_shape.isInside((notch_center_x, notch_center_y, notch_center_z)), \
            "Notch center should be outside (void in) the U-shape solid"
    
        # Verify a point in the U base is inside the solid
        base_center_x = 0.0
        base_center_y = (y_bot + y_notch_bot) / 2  # (-20 + -5)/2 = -12.5
        base_center_z = H / 2
        assert solid_shape.isInside((base_center_x, base_center_y, base_center_z)), \
            "U base center should be inside the solid"
    
        # Verify a point in the left square (outside U) is inside the solid
        left_sq_outer_x = -38.0   # well inside left square, outside U
        left_sq_outer_y = -27.0   # well inside left square, outside U
        assert solid_shape.isInside((left_sq_outer_x, left_sq_outer_y, H / 2)), \
            "Left square outer region should be inside the solid"
    
        # Verify a point in the right square (outside U) is inside the solid
        right_sq_outer_x = 38.0   # well inside right square, outside U
        assert solid_shape.isInside((right_sq_outer_x, left_sq_outer_y, H / 2)), \
            "Right square outer region should be inside the solid"
    
        # Verify symmetry: center of mass should be at x≈0 (symmetric about YZ plane)
        com = cq.Shape.centerOfMass(solid_shape)
        assert abs(com.x) < TOL, f"Center of mass X should be ~0 (symmetric), got {com.x}"
    
        # Verify left arm of U is solid
        assert solid_shape.isInside((-25.0, 5.0, H / 2)), \
            "Left arm of U should be inside the solid"
    
        # Verify right arm of U is solid
        assert solid_shape.isInside((25.0, 5.0, H / 2)), \
            "Right arm of U should be inside the solid"
    
        # Verify a point outside the entire object is not inside
        assert not solid_shape.isInside((0.0, -25.0, H / 2)), \
            "Point below U base and outside squares should not be inside the solid"
    
        # Verify the squares are at the correct Z range
        assert solid_shape.isInside((-38.0, -27.0, 1.0)), \
            "Left square should exist near Z=0"
        assert solid_shape.isInside((-38.0, -27.0, H - 1.0)), \
            "Left square should exist near Z=H"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00300037/gpt_generated.stl')
