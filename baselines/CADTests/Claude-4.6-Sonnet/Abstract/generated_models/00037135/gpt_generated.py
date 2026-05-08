import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        leg_w   = 4    # width of each leg
        left_h  = 20   # full height of left leg (the tall vertical stroke of 'h')
        right_h = 10   # height of right leg (lower portion of 'h')
        bar_h   = 4    # height of crossbar (the horizontal stroke of 'h')
        gap     = 16   # horizontal gap between the two legs (inner distance)
        depth   = 30   # extrusion depth along Z-axis
    
        # Derived dimensions
        total_w   = leg_w + gap + leg_w  # = 24
        bar_y_bot = right_h              # crossbar bottom at y=10
        bar_y_top = right_h + bar_h      # crossbar top at y=14
    
        # --- Step 1: Build the 'h' profile using union of three rectangular boxes ---
        # The letter 'h' consists of:
        #   - Left vertical stroke: full height (left leg)
        #   - Horizontal crossbar: at mid-height, spanning full width
        #   - Right vertical stroke: lower portion only (right leg, below crossbar)
    
        # Left leg: x=0..leg_w, y=0..left_h, z=0..depth
        left_leg = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, 0))
            .box(leg_w, left_h, depth, centered=False)
        )
    
        # Crossbar: x=0..total_w, y=bar_y_bot..bar_y_top, z=0..depth
        crossbar = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, bar_y_bot, 0))
            .box(total_w, bar_h, depth, centered=False)
        )
    
        # Right leg: x=(total_w-leg_w)..total_w, y=0..right_h, z=0..depth
        right_leg = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(total_w - leg_w, 0, 0))
            .box(leg_w, right_h, depth, centered=False)
        )
    
        # --- Step 2: Union the three parts into one solid bench ---
        result = left_leg.union(crossbar).union(right_leg)
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - total_w) < TOL, \
            f"X length: expected {total_w}, got {bb.xlen}"
        assert abs(bb.ylen - left_h) < TOL, \
            f"Y length: expected {left_h}, got {bb.ylen}"
        assert abs(bb.zlen - depth) < TOL, \
            f"Z length: expected {depth}, got {bb.zlen}"
    
        # Bounding box origin
        assert abs(bb.xmin - 0) < TOL, f"xmin: expected 0, got {bb.xmin}"
        assert abs(bb.ymin - 0) < TOL, f"ymin: expected 0, got {bb.ymin}"
        assert abs(bb.zmin - 0) < TOL, f"zmin: expected 0, got {bb.zmin}"
    
        # Volume check using inclusion-exclusion:
        # Left leg volume:  leg_w * left_h * depth = 4 * 20 * 30 = 2400
        # Crossbar volume:  total_w * bar_h * depth = 24 * 4 * 30 = 2880
        # Right leg volume: leg_w * right_h * depth = 4 * 10 * 30 = 1200
        #
        # Overlaps:
        #   left_leg ∩ crossbar:  x=0..4, y=10..14, z=0..30 → 4*4*30 = 480
        #   right_leg ∩ crossbar: right leg y=0..10, crossbar y=10..14
        #                         → they share only the plane y=10 (zero volume)
        #   left_leg ∩ right_leg: no x overlap → 0
        #
        # Total = 2400 + 2880 + 1200 - 480 - 0 - 0 = 6000
        vol_left    = leg_w * left_h * depth
        vol_cross   = total_w * bar_h * depth
        vol_right   = leg_w * right_h * depth
        overlap_lc  = leg_w * bar_h * depth   # left_leg ∩ crossbar
        overlap_rc  = 0                        # right_leg ∩ crossbar (share only a face)
        expected_vol = vol_left + vol_cross + vol_right - overlap_lc - overlap_rc
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Check that a point inside the left leg is inside the solid
        left_leg_pt = (leg_w / 2, left_h / 2, depth / 2)
        assert result.val().isInside(left_leg_pt), \
            f"Point {left_leg_pt} should be inside left leg"
    
        # Check that a point inside the crossbar (middle section) is inside the solid
        crossbar_pt = (total_w / 2, (bar_y_bot + bar_y_top) / 2, depth / 2)
        assert result.val().isInside(crossbar_pt), \
            f"Point {crossbar_pt} should be inside crossbar"
    
        # Check that a point inside the right leg is inside the solid
        right_leg_pt = (total_w - leg_w / 2, right_h / 2, depth / 2)
        assert result.val().isInside(right_leg_pt), \
            f"Point {right_leg_pt} should be inside right leg"
    
        # Check that a point in the gap (below crossbar, between legs) is NOT inside
        gap_pt = (total_w / 2, right_h / 2, depth / 2)
        assert not result.val().isInside(gap_pt), \
            f"Point {gap_pt} should NOT be inside (it's in the gap of the 'h')"
    
        # Check that a point above the crossbar on the right side is NOT inside
        above_bar_pt = (total_w - leg_w / 2, left_h - 1, depth / 2)
        assert not result.val().isInside(above_bar_pt), \
            f"Point {above_bar_pt} should NOT be inside (above crossbar on right side)"
    
        # Check exactly 1 solid
        solid_count = result.solids().size()
        assert solid_count == 1, f"Solid count: expected 1, got {solid_count}"
    
        print(f"All assertions passed!")
        print(f"Bench dimensions: {total_w}W x {left_h}H x {depth}D")
        print(f"Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00037135/gpt_generated.stl')
