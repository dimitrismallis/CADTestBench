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
        L = 0.03547       # length (X)
        W = 1.27689       # width (Y)
        H = 0.14188       # height (Z)
    
        hole_L = 0.03547      # hole length (X) - same as plate
        hole_W = 0.5677508    # hole width (Y)
        hole_H = 0.094585     # hole depth (Z)
    
        padding = 0.047292    # spacing from holes to outer edges
    
        # --- Step 1: Create base plate centered at origin ---
        base = cq.Workplane("XY").box(L, W, H)
    
        # --- Step 2: Compute hole positions ---
        # Two holes symmetric about Y=0
        # Left hole: left edge at -W/2 + padding, so center at -W/2 + padding + hole_W/2
        # Right hole: right edge at W/2 - padding, so center at W/2 - padding - hole_W/2
        left_y  = -W/2 + padding + hole_W/2
        right_y =  W/2 - padding - hole_W/2
    
        # Actual gap between the two holes
        gap_between = right_y - left_y - hole_W  # = W - 2*padding - 2*hole_W
    
        # --- Step 3: Create hole cutters as separate boxes ---
        # Holes cut from top (Z = H/2) downward by hole_H
        # Hole cutter box centered at Z = H/2 - hole_H/2
        hole_z_center = H/2 - hole_H/2
    
        left_hole = (
            cq.Workplane("XY")
            .box(hole_L, hole_W, hole_H)
            .translate((0, left_y, hole_z_center))
        )
    
        right_hole = (
            cq.Workplane("XY")
            .box(hole_L, hole_W, hole_H)
            .translate((0, right_y, hole_z_center))
        )
    
        # --- Step 4: Cut holes from base plate ---
        result = base.cut(left_hole).cut(right_hole)
    
        # --- Step 5: Translate the final part ---
        # y-offset = 0.111555, z stays centered (bounding box center at 0)
        y_offset = 0.111555
        z_offset = 0.0
        result = result.translate((0, y_offset, z_offset))
    
        # --- Final object verification ---
        TOL = 1e-4
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Check overall bounding box dimensions
        assert abs(bb.xlen - L) < TOL, \
            f"X length: expected {L}, got {bb.xlen}"
        assert abs(bb.ylen - W) < TOL, \
            f"Y width: expected {W}, got {bb.ylen}"
        assert abs(bb.zlen - H) < TOL, \
            f"Z height: expected {H}, got {bb.zlen}"
    
        # Check bounding box Z is centered at 0
        z_bb_center = (bb.zmin + bb.zmax) / 2.0
        assert abs(z_bb_center - 0.0) < TOL, \
            f"Z bounding box center: expected 0.0, got {z_bb_center}"
    
        # Check bounding box Y center is at y_offset
        y_bb_center = (bb.ymin + bb.ymax) / 2.0
        assert abs(y_bb_center - y_offset) < TOL, \
            f"Y bounding box center: expected {y_offset}, got {y_bb_center}"
    
        # Check volume: base plate minus two holes
        base_vol = L * W * H
        hole_vol_each = hole_L * hole_W * hole_H
        hole_vol_total = 2 * hole_vol_each
        expected_vol = base_vol - hole_vol_total
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that holes exist: volume should be less than base plate
        assert actual_vol < base_vol, \
            "Volume should be less than base plate (holes exist)"
    
        # Check center of mass Z (holes removed from top shift CM downward)
        expected_cm_z = (0.0 - 2 * hole_vol_each * hole_z_center) / expected_vol
        center = solid.Center()
        assert abs(center.z - expected_cm_z) < TOL, \
            f"Z center of mass: expected {expected_cm_z:.6f}, got {center.z:.6f}"
    
        # Check center of mass Y (symmetric holes, translated by y_offset)
        assert abs(center.y - y_offset) < TOL, \
            f"Y center of mass: expected {y_offset}, got {center.y}"
    
        # Check hole positions: points inside holes should be outside the solid
        left_hole_top  = (0, left_y  + y_offset, H/2 - hole_H/4)
        right_hole_top = (0, right_y + y_offset, H/2 - hole_H/4)
    
        assert not solid.isInside(left_hole_top), \
            f"Left hole top point should be outside solid (in hole)"
        assert not solid.isInside(right_hole_top), \
            f"Right hole top point should be outside solid (in hole)"
    
        # Points at the bottom of the plate (below holes) should be inside solid
        left_bottom  = (0, left_y  + y_offset, -H/4)
        right_bottom = (0, right_y + y_offset, -H/4)
    
        assert solid.isInside(left_bottom), \
            f"Left bottom point should be inside solid"
        assert solid.isInside(right_bottom), \
            f"Right bottom point should be inside solid"
    
        # Check symmetry: holes should be symmetric about y=0 (before translation)
        assert abs(left_y + right_y) < TOL, \
            f"Holes should be symmetric about Y=0: left_y={left_y:.6f}, right_y={right_y:.6f}"
    
        # Check padding from outer edges (left and right)
        left_edge_dist  = left_y  - (-W/2) - hole_W/2
        right_edge_dist = W/2 - right_y - hole_W/2
    
        assert abs(left_edge_dist - padding) < TOL, \
            f"Left edge padding: expected {padding}, got {left_edge_dist}"
        assert abs(right_edge_dist - padding) < TOL, \
            f"Right edge padding: expected {padding}, got {right_edge_dist}"
    
        # Check gap between holes is positive (holes don't touch each other)
        assert gap_between > 0, \
            f"Gap between holes must be positive, got {gap_between}"
    
        # Check gap is approximately the stated padding (~0.047292)
        # Actual gap = W - 2*padding - 2*hole_W
        expected_gap = W - 2*padding - 2*hole_W
        assert abs(gap_between - expected_gap) < TOL, \
            f"Gap between holes: expected {expected_gap:.6f}, got {gap_between:.6f}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.5f} x {bb.ylen:.5f} x {bb.zlen:.5f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Center of mass: ({center.x:.5f}, {center.y:.5f}, {center.z:.5f})")
        print(f"Hole positions: left_y={left_y:.5f}, right_y={right_y:.5f}")
        print(f"Padding (edges): left={left_edge_dist:.6f}, right={right_edge_dist:.6f}")
        print(f"Gap between holes: {gap_between:.6f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00521437/gpt_generated.stl')
