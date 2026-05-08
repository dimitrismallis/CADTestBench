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
        length = 0.337772   # X dimension
        width  = 0.75       # Y dimension
        height = 0.021792   # Z extrusion height
        margin = 0.01816    # side and top margin
    
        # --- Derived dimensions ---
        # U-shape: open at top, bottom bar = margin thick, side arms = margin thick
        cutout_x = length - 2 * margin   # inner width of cutout
        cutout_y = width  - margin        # inner height of cutout (open at top)
    
        # Cutout center Y: bottom of cutout at -width/2 + margin, top at width/2
        # cutout_center_y = midpoint = margin/2
        cutout_center_y = margin / 2
    
        # Inner cutout bounds:
        ix_left   = -cutout_x / 2
        ix_right  =  cutout_x / 2
        iy_bottom = cutout_center_y - cutout_y / 2  # = -width/2 + margin
        iy_top    = cutout_center_y + cutout_y / 2  # = width/2 (flush with outer top)
    
        # --- Step 1: Build U-shape as closed 8-vertex wire, then extrude ---
        # The profile: outer rectangle with a rectangular notch cut from the top center
        # Going CCW: bottom-left → bottom-right → top-right → inner-top-right →
        #            inner-bottom-right → inner-bottom-left → inner-top-left → top-left → close
        result = (
            cq.Workplane("XY")
            .moveTo(-length/2, -width/2)      # P1: bottom-left outer
            .lineTo( length/2, -width/2)      # P2: bottom-right outer
            .lineTo( length/2,  width/2)      # P3: top-right outer
            .lineTo( ix_right,  iy_top)       # P4: top-right inner (= width/2, collinear with P3→top)
            .lineTo( ix_right,  iy_bottom)    # P5: bottom-right inner
            .lineTo( ix_left,   iy_bottom)    # P6: bottom-left inner
            .lineTo( ix_left,   iy_top)       # P7: top-left inner
            .lineTo(-length/2,  width/2)      # P8: top-left outer
            .close()
            .extrude(height)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box should match outer dimensions
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Volume: U-shape area × height
        outer_area   = length * width
        cutout_area  = cutout_x * cutout_y
        u_area       = outer_area - cutout_area
        expected_vol = u_area * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that a point inside the cutout is NOT inside the solid
        cutout_test_point = (0.0, cutout_center_y, height / 2)
        assert not result.val().isInside(cutout_test_point), \
            f"Point {cutout_test_point} should be outside (in cutout), but is inside"
    
        # A point in the bottom bar of the U should be inside
        bottom_bar_y = -width / 2 + margin / 4
        bottom_test_point = (0.0, bottom_bar_y, height / 2)
        assert result.val().isInside(bottom_test_point), \
            f"Point {bottom_test_point} should be inside (bottom bar), but is outside"
    
        # A point in the left arm of the U should be inside
        left_arm_x = -length / 2 + margin / 2
        left_test_point = (left_arm_x, 0.0, height / 2)
        assert result.val().isInside(left_test_point), \
            f"Point {left_test_point} should be inside (left arm), but is outside"
    
        # A point in the right arm of the U should be inside
        right_arm_x = length / 2 - margin / 2
        right_test_point = (right_arm_x, 0.0, height / 2)
        assert result.val().isInside(right_test_point), \
            f"Point {right_test_point} should be inside (right arm), but is outside"
    
        # Face count:
        # Profile has 8 edges (8 vertices + close) → 8 side faces
        # + 1 top face + 1 bottom face = 10 total
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00672098/gpt_generated.stl')
