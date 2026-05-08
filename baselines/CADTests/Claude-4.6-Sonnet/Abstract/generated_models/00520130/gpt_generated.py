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
        sq_size = 50.0   # main square side length
        height  = 20.0   # extrusion height
        rect_w  = 10.0   # width of side rectangles (~1/5 of sq_size)
        rect_l  = 50.0   # length of side rectangles (same as square)
        overlap = 1.0    # small overlap so fuse creates a true single solid
    
        # --- Step 1: Main square extruded upward (+Z), from Z=0 to Z=+20 ---
        main_body = (
            cq.Workplane("XY")
            .rect(sq_size, sq_size)
            .extrude(height)
        )
    
        # --- Step 2: Left rectangle extruded downward (-Z) with slight overlap ---
        # Occupies Z = -height to +overlap, centered at left_x, 0
        # We build it from Z=0 upward by (height + overlap), then translate down by height
        left_x = -(sq_size / 2 + rect_w / 2)   # = -30
        left_rect = (
            cq.Workplane("XY")
            .center(left_x, 0)
            .rect(rect_w, rect_l)
            .extrude(height + overlap)           # height + overlap tall
            .translate((0, 0, -height))          # shift so it spans Z=-20 to Z=+overlap
        )
    
        # --- Step 3: Right rectangle extruded downward (-Z) with slight overlap ---
        right_x = +(sq_size / 2 + rect_w / 2)  # = +30
        right_rect = (
            cq.Workplane("XY")
            .center(right_x, 0)
            .rect(rect_w, rect_l)
            .extrude(height + overlap)
            .translate((0, 0, -height))
        )
    
        # --- Step 4: Fuse all three bodies using Shape-level boolean union ---
        # With volumetric overlap, fuse should produce a true single solid
        main_solid  = main_body.val()
        left_solid  = left_rect.val()
        right_solid = right_rect.val()
    
        fused = main_solid.fuse(left_solid, glue=False, tol=1e-3)
        fused = fused.fuse(right_solid, glue=False, tol=1e-3)
    
        # Wrap back into a Workplane
        result = cq.Workplane("XY").add(fused)
    
        # --- Final object verification ---
        TOL = 0.5  # slightly relaxed due to overlap
    
        bb = result.val().BoundingBox()
    
        # Overall bounding box:
        # X: -35 to +35 => xlen = 70
        # Y: -25 to +25 => ylen = 50
        # Z: -20 to +20 (the overlap region is inside the main body, so zmax stays ~20)
        expected_xlen = sq_size + 2 * rect_w   # 70
        expected_ylen = sq_size                 # 50
        expected_zlen = 2 * height             # 40 (zmin=-20, zmax=+20)
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"BBox X: expected {expected_xlen}, got {bb.xlen}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"BBox Y: expected {expected_ylen}, got {bb.ylen}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"BBox Z: expected {expected_zlen}, got {bb.zlen}"
    
        # X extents
        assert abs(bb.xmin - (-35)) < TOL, f"xmin: expected -35, got {bb.xmin}"
        assert abs(bb.xmax - (+35)) < TOL, f"xmax: expected +35, got {bb.xmax}"
    
        # Z extents
        assert abs(bb.zmin - (-height)) < TOL, f"zmin: expected {-height}, got {bb.zmin}"
        assert abs(bb.zmax - (+height)) < TOL, f"zmax: expected {+height}, got {bb.zmax}"
    
        # Volume check:
        # main square:  50 * 50 * 20 = 50000
        # left rect:    10 * 50 * (20+1) = 10500, but overlap region 10*50*1=500 is inside main
        # right rect:   same = 10500, overlap 500 inside main
        # Total unique volume = 50000 + 10*50*20 + 10*50*20 = 70000
        expected_vol = sq_size * sq_size * height + 2 * (rect_w * rect_l * height)
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # The shape should be a single fused solid
        n_solids = result.solids().size()
        assert n_solids == 1, \
            f"Solids: expected 1, got {n_solids}"
    
        # Containment checks
        assert result.val().isInside((0, 0, 10)), \
            "Point (0,0,10) should be inside main body"
        assert result.val().isInside((left_x, 0, -10)), \
            f"Point ({left_x},0,-10) should be inside left flange"
        assert result.val().isInside((right_x, 0, -10)), \
            f"Point ({right_x},0,-10) should be inside right flange"
    
        # The groove: center below Z=0 should NOT be inside
        assert not result.val().isInside((0, 0, -10)), \
            "Point (0,0,-10) should NOT be inside (it's in the groove)"
    
        # Fully outside
        assert not result.val().isInside((0, 0, 30)), \
            "Point (0,0,30) should NOT be inside"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00520130/gpt_generated.stl')
