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
        rect_length = 160.0      # long dimension
        rect_width  = 20.0       # short dimension
        rect_height = 4.0        # extrusion height (small amount)
    
        sq_side     = rect_length / 16.0   # = 10.0  (square side = 1/16 of length)
        sq_width    = rect_width           # = 20.0  (same width as rectangle)
        sq_height   = rect_height / 3.0    # = 4/3 ≈ 1.333 (1/3 of extrusion)
    
        # --- Step 1: Main long rectangle extruded ---
        # Centered at origin: X in [-80, 80], Y in [-10, 10], Z in [-2, 2]
        result = cq.Workplane("XY").box(rect_length, rect_width, rect_height)
    
        # --- Step 2: Left tab (square cross-section) at -X short edge ---
        # Tab: sq_side × sq_width × sq_height
        # Centered at X = -(rect_length/2 + sq_side/2), Y=0, Z=0 (centered in Z)
        left_tab = (
            cq.Workplane("XY")
            .box(sq_side, sq_width, sq_height)
            .translate((-(rect_length / 2 + sq_side / 2), 0, 0))
        )
    
        # --- Step 3: Right tab (square cross-section) at +X short edge ---
        right_tab = (
            cq.Workplane("XY")
            .box(sq_side, sq_width, sq_height)
            .translate((rect_length / 2 + sq_side / 2, 0, 0))
        )
    
        # --- Step 4: Union all three parts ---
        result = result.union(left_tab).union(right_tab)
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # Overall bounding box:
        # X: from -(80+10) to +(80+10) = -90 to +90 → xlen = 180
        # Y: -10 to +10 → ylen = 20
        # Z: -2 to +2 → zlen = 4
        expected_xlen = rect_length + 2 * sq_side   # 160 + 20 = 180
        expected_ylen = rect_width                   # 20
        expected_zlen = rect_height                  # 4 (tabs are shorter, main body dominates)
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"Overall X length: expected {expected_xlen}, got {bb.xlen}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Overall Y length: expected {expected_ylen}, got {bb.ylen}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Overall Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Volume check:
        # Main box: 160 × 20 × 4 = 12800
        # Each tab: 10 × 20 × (4/3) = 800/3 ≈ 266.667
        # Total: 12800 + 2 * 266.667 = 13333.333
        vol_main = rect_length * rect_width * rect_height
        vol_tab  = sq_side * sq_width * sq_height
        expected_vol = vol_main + 2 * vol_tab
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.3f}, got {actual_vol:.3f}"
    
        # Check tabs are present: the object should extend beyond the main rectangle in X
        assert bb.xmin < -(rect_length / 2) - TOL, \
            f"Left tab missing: xmin={bb.xmin} should be < {-(rect_length/2)}"
        assert bb.xmax > (rect_length / 2) + TOL, \
            f"Right tab missing: xmax={bb.xmax} should be > {rect_length/2}"
    
        # Check symmetry: center of bounding box should be near origin
        center = result.val().CenterOfBoundBox()
        assert abs(center.x) < TOL, f"X symmetry: center.x={center.x}, expected ~0"
        assert abs(center.y) < TOL, f"Y symmetry: center.y={center.y}, expected ~0"
        assert abs(center.z) < TOL, f"Z symmetry: center.z={center.z}, expected ~0"
    
        # Check tab height is 1/3 of main extrusion
        assert abs(sq_height - rect_height / 3) < TOL, \
            f"Tab height: expected {rect_height/3}, got {sq_height}"
    
        # Check tab side is 1/16 of rectangle length
        assert abs(sq_side - rect_length / 16) < TOL, \
            f"Tab side: expected {rect_length/16}, got {sq_side}"
    
        # Check tab width equals rectangle width
        assert abs(sq_width - rect_width) < TOL, \
            f"Tab width: expected {rect_width}, got {sq_width}"
    
        # The object should have exactly 1 solid (all unioned)
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00672272/gpt_generated.stl')
