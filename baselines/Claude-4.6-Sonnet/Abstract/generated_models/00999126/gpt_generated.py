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
        rect_width  = 60.0   # width of the base rectangle (3 × height)
        rect_height = 20.0   # height of the base rectangle
        depth       = 5.0    # extrusion depth (small)
    
        # Cutout dimensions
        right_cutout_h = 4.0    # height of right cutout
        left_cutout_h  = 12.0   # height of left cutout (3× right)
        cutout_depth   = 8.0    # how far each cutout goes inward from the edge
    
        # Half dimensions
        hw = rect_width  / 2   # 30
        hh = rect_height / 2   # 10
    
        # --- Step 1: Base rectangle extruded ---
        base = cq.Workplane("XY").box(rect_width, rect_height, depth)
    
        # --- Step 2: Left cutout box ---
        # Centered on left edge: x from -hw to (-hw + cutout_depth), y centered at 0
        # Box center: x = -hw + cutout_depth/2, y = 0, z = 0
        left_cut = cq.Workplane("XY").box(cutout_depth, left_cutout_h, depth)
        left_cut = left_cut.translate((-hw + cutout_depth / 2, 0, 0))
    
        # --- Step 3: Right cutout box ---
        # Centered on right edge: x from (hw - cutout_depth) to hw, y centered at 0
        # Box center: x = hw - cutout_depth/2, y = 0, z = 0
        right_cut = cq.Workplane("XY").box(cutout_depth, right_cutout_h, depth)
        right_cut = right_cut.translate((hw - cutout_depth / 2, 0, 0))
    
        # --- Step 4: Subtract cutouts from base ---
        result = base.cut(left_cut).cut(right_cut)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - rect_width)  < TOL, \
            f"X length: expected {rect_width}, got {bb.xlen}"
        assert abs(bb.ylen - rect_height) < TOL, \
            f"Y length: expected {rect_height}, got {bb.ylen}"
        assert abs(bb.zlen - depth)       < TOL, \
            f"Z depth: expected {depth}, got {bb.zlen}"
    
        # Width is 3× height
        assert abs(bb.xlen / bb.ylen - 3.0) < TOL, \
            f"Width/Height ratio: expected 3.0, got {bb.xlen/bb.ylen}"
    
        # Left cutout is 3× longer than right cutout
        assert abs(left_cutout_h / right_cutout_h - 3.0) < TOL, \
            f"Left/Right cutout ratio: expected 3.0, got {left_cutout_h/right_cutout_h}"
    
        # Volume check: base rectangle minus two cutouts, extruded
        base_area      = rect_width * rect_height
        left_cut_area  = cutout_depth * left_cutout_h
        right_cut_area = cutout_depth * right_cutout_h
        expected_area  = base_area - left_cut_area - right_cut_area
        expected_vol   = expected_area * depth
        actual_vol     = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Check that the left cutout region is NOT inside the solid
        left_cut_center = (-hw + cutout_depth / 2, 0.0, 0.0)
        assert not result.val().isInside(left_cut_center), \
            f"Left cutout center should be outside the solid: {left_cut_center}"
    
        # Check that the right cutout region is NOT inside the solid
        right_cut_center = (hw - cutout_depth / 2, 0.0, 0.0)
        assert not result.val().isInside(right_cut_center), \
            f"Right cutout center should be outside the solid: {right_cut_center}"
    
        # Check that the body center IS inside the solid
        body_center = (0.0, 0.0, 0.0)
        assert result.val().isInside(body_center), \
            f"Body center should be inside the solid: {body_center}"
    
        # Check that a point in the middle of the left edge (outside cutout) IS inside
        left_edge_mid_outside = (-hw + cutout_depth / 2, hh - 1.0, 0.0)
        assert result.val().isInside(left_edge_mid_outside), \
            f"Point above left cutout should be inside solid: {left_edge_mid_outside}"
    
        print(f"All assertions passed!")
        print(f"  Bounding box: {bb.xlen} x {bb.ylen} x {bb.zlen}")
        print(f"  Volume: {actual_vol:.2f} mm³ (expected {expected_vol:.2f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00999126/gpt_generated.stl')
