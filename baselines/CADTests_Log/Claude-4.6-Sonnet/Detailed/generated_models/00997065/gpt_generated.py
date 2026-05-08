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
        sq_len   = 1.1056      # square length (X-direction)
        sq_wid   = 1.22951     # square width  (Y-direction)
        rect_len = 1.76342     # rectangle length (X-direction, how far it extends)
        rect_w   = 0.368852    # rectangle width
        rect_h   = 2 * rect_w  # rectangle height (Y-direction) = 0.737704
        extrude_depth = 0.122951
    
        # --- Step 1: Build the central square ---
        # Centered at origin: X from -sq_len/2 to +sq_len/2, Y from -sq_wid/2 to +sq_wid/2
        sq_x = sq_len / 2   # 0.5528
        sq_y = sq_wid / 2   # 0.614755
    
        # --- Step 2: Build left and right rectangles ---
        # Each rectangle: X-extent = rect_len, Y-extent = rect_h
        # Centered along horizontal centerline (Y=0)
        # Left rectangle: attached to left edge of square, extending left
        #   X from -(sq_x + rect_len) to -sq_x
        # Right rectangle: attached to right edge of square, extending right
        #   X from +sq_x to +(sq_x + rect_len)
        rect_half_h = rect_h / 2   # 0.368852
    
        # --- Step 3: Create the combined 2D profile using a closed wire ---
        # Build the profile as a union of three rectangles using Workplane
        # Central square
        central = cq.Workplane("XY").rect(sq_len, sq_wid)
    
        # Left rectangle center: x = -(sq_x + rect_len/2), y = 0
        left_cx = -(sq_x + rect_len / 2)
        left_rect = cq.Workplane("XY").center(left_cx, 0).rect(rect_len, rect_h)
    
        # Right rectangle center: x = +(sq_x + rect_len/2), y = 0
        right_cx = (sq_x + rect_len / 2)
        right_rect = cq.Workplane("XY").center(right_cx, 0).rect(rect_len, rect_h)
    
        # --- Step 4: Extrude each part and union them ---
        central_solid = cq.Workplane("XY").rect(sq_len, sq_wid).extrude(extrude_depth)
        left_solid    = cq.Workplane("XY").center(left_cx, 0).rect(rect_len, rect_h).extrude(extrude_depth)
        right_solid   = cq.Workplane("XY").center(right_cx, 0).rect(rect_len, rect_h).extrude(extrude_depth)
    
        result = central_solid.union(left_solid).union(right_solid)
    
        # --- Final object verification ---
        TOL = 0.001
    
        bb = result.val().BoundingBox()
    
        # Overall X extent: sq_len + 2 * rect_len
        expected_xlen = sq_len + 2 * rect_len
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen:.6f}, got {bb.xlen:.6f}"
    
        # Overall Y extent: sq_wid (the square is taller than the rectangles since sq_wid=1.22951 > rect_h=0.737704)
        expected_ylen = sq_wid
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen:.6f}, got {bb.ylen:.6f}"
    
        # Overall Z extent: extrude_depth
        expected_zlen = extrude_depth
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen:.6f}, got {bb.zlen:.6f}"
    
        # Volume: central square + 2 side rectangles (no overlap since they share edges only)
        vol_central = sq_len * sq_wid * extrude_depth
        vol_rect    = rect_len * rect_h * extrude_depth
        expected_vol = vol_central + 2 * vol_rect
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Z bounds: from 0 to extrude_depth (box is centered=True by default in Z? No, extrude goes +Z)
        # Actually extrude goes from 0 to extrude_depth
        assert abs(bb.zmin - 0.0) < TOL, f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - extrude_depth) < TOL, f"Z max: expected {extrude_depth}, got {bb.zmax}"
    
        # Center of bounding box X should be ~0 (symmetric)
        cx = (bb.xmin + bb.xmax) / 2
        assert abs(cx) < TOL, f"X center: expected 0, got {cx}"
    
        # Center of bounding box Y should be ~0 (symmetric)
        cy = (bb.ymin + bb.ymax) / 2
        assert abs(cy) < TOL, f"Y center: expected 0, got {cy}"
    
        # Check that the shape has cylindrical faces = 0 (all planar)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # The shape should be a single solid
        n_solids = result.solids().size()
        assert n_solids == 1, f"Expected 1 solid, got {n_solids}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: X={bb.xlen:.6f}, Y={bb.ylen:.6f}, Z={bb.zlen:.6f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00997065/gpt_generated.stl')
