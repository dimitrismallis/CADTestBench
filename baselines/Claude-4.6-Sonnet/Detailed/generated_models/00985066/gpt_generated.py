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
        # --- Parameters (in meters, treated as mm-scale units) ---
        col_len   = 0.05    # column length (X direction)
        col_wid   = 0.35    # column width (Y direction)
        col_h     = 0.725   # column height (Z direction)
    
        bar_len   = 1.175   # horizontal bar length (X direction)
        bar_wid   = 0.35    # horizontal bar width (Y direction)
        bar_h     = 0.025   # horizontal bar height (Z direction)
    
        # --- Step 1: Horizontal bar (sits at the top, z from col_h to col_h + bar_h) ---
        bar = (
            cq.Workplane("XY")
            .box(bar_len, bar_wid, bar_h, centered=(True, True, False))
            .translate((0, 0, col_h))
        )
    
        # --- Step 2: Left column (x from -bar_len/2 to -bar_len/2 + col_len) ---
        left_col_x_center = -bar_len / 2.0 + col_len / 2.0  # = -0.5875 + 0.025 = -0.5625
        left_col = (
            cq.Workplane("XY")
            .box(col_len, col_wid, col_h, centered=(True, True, False))
            .translate((left_col_x_center, 0, 0))
        )
    
        # --- Step 3: Right column (x from bar_len/2 - col_len to bar_len/2) ---
        right_col_x_center = bar_len / 2.0 - col_len / 2.0  # = 0.5875 - 0.025 = 0.5625
        right_col = (
            cq.Workplane("XY")
            .box(col_len, col_wid, col_h, centered=(True, True, False))
            .translate((right_col_x_center, 0, 0))
        )
    
        # --- Step 4: Union all three parts ---
        result = bar.union(left_col).union(right_col)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - bar_len) < TOL, \
            f"X length: expected {bar_len}, got {bb.xlen}"
        assert abs(bb.ylen - bar_wid) < TOL, \
            f"Y width: expected {bar_wid}, got {bb.ylen}"
        expected_total_h = col_h + bar_h  # 0.725 + 0.025 = 0.750
        assert abs(bb.zlen - expected_total_h) < TOL, \
            f"Z height: expected {expected_total_h}, got {bb.zlen}"
    
        # Z extents: bottom at 0, top at 0.750
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - expected_total_h) < TOL, \
            f"Z max: expected {expected_total_h}, got {bb.zmax}"
    
        # X extents: centered, so -bar_len/2 to +bar_len/2
        assert abs(bb.xmin - (-bar_len / 2)) < TOL, \
            f"X min: expected {-bar_len/2}, got {bb.xmin}"
        assert abs(bb.xmax - (bar_len / 2)) < TOL, \
            f"X max: expected {bar_len/2}, got {bb.xmax}"
    
        # Y extents: centered, so -bar_wid/2 to +bar_wid/2
        assert abs(bb.ymin - (-bar_wid / 2)) < TOL, \
            f"Y min: expected {-bar_wid/2}, got {bb.ymin}"
        assert abs(bb.ymax - (bar_wid / 2)) < TOL, \
            f"Y max: expected {bar_wid/2}, got {bb.ymax}"
    
        # Volume check:
        # Columns (z=0..0.725) and bar (z=0.725..0.750) are vertically stacked — no overlap.
        # Total volume = 2 * column_volume + bar_volume
        col_vol      = col_len * col_wid * col_h   # 0.05 * 0.35 * 0.725 = 0.0126875
        bar_vol      = bar_len * bar_wid * bar_h   # 1.175 * 0.35 * 0.025 = 0.01028125
        expected_vol = 2 * col_vol + bar_vol       # 0.0253750 + 0.01028125 = 0.03565625
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # The union should produce a single solid
        solids = result.solids().size()
        assert solids == 1, \
            f"Expected 1 solid after union, got {solids}"
    
        # Check symmetry: center of mass should be at x=0, y=0
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, \
            f"Center of mass X should be 0, got {com.x}"
        assert abs(com.y) < TOL, \
            f"Center of mass Y should be 0, got {com.y}"
    
        # Check that the interior gap (between columns, below the bar) is hollow
        # A point at center x, center y, halfway up the columns should be OUTSIDE
        mid_z = col_h / 2.0  # halfway up the columns
        interior_point = (0.0, 0.0, mid_z)
        is_inside = result.val().isInside(interior_point)
        assert not is_inside, \
            f"Interior gap between columns should be empty, but point {interior_point} is inside"
    
        # A point inside the left column should be inside the solid
        left_col_point = (left_col_x_center, 0.0, col_h / 2.0)
        assert result.val().isInside(left_col_point), \
            f"Point inside left column {left_col_point} should be inside the solid"
    
        # A point inside the right column should be inside the solid
        right_col_point = (right_col_x_center, 0.0, col_h / 2.0)
        assert result.val().isInside(right_col_point), \
            f"Point inside right column {right_col_point} should be inside the solid"
    
        # A point inside the bar should be inside the solid
        bar_point = (0.0, 0.0, col_h + bar_h / 2.0)
        assert result.val().isInside(bar_point), \
            f"Point inside bar {bar_point} should be inside the solid"
    
        # Check column dimensions via faces intersected by a vertical line through left column
        # The left column spans z=0 to z=0.725; the bar spans z=0.725 to z=0.750
        # A line through the left column center should intersect bottom and top faces
        left_faces = result.val().facesIntersectedByLine(
            (left_col_x_center, 0.0, -1.0), (0, 0, 1)
        )
        assert len(left_faces) >= 2, \
            f"Expected at least 2 faces intersected by vertical line through left column, got {len(left_faces)}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00985066/gpt_generated.stl')
