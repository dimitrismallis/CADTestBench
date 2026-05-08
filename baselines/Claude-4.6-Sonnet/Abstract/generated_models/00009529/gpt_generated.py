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
        # Base rectangle: length=60, width=20, height=5
        rect_length = 60.0
        rect_width  = 20.0
        rect_height = 5.0
    
        # Right square: side=20, extrusion=10
        right_side   = 20.0
        right_height = 10.0
    
        # Left square: side=10 (25% of right area: 100 = 0.25*400), extrusion=5
        left_side   = 10.0
        left_height = 5.0   # right_height = 2 * left_height ✓
    
        # --- Step 1: Base extruded rectangle, centered at origin ---
        # Spans x: -30..+30, y: -10..+10, z: 0..5
        base = (
            cq.Workplane("XY")
            .rect(rect_length, rect_width)
            .extrude(rect_height)
        )
    
        # --- Step 2: Right square, connected to right edge of rectangle ---
        # Rectangle right edge at x=+30. Right square side=20, centered in Y.
        # Square spans x: 30..50, y: -10..10, z: 0..10
        # Center of right square: x = 30 + 20/2 = 40, y = 0
        right_sq = (
            cq.Workplane("XY")
            .center(rect_length/2 + right_side/2, 0)
            .rect(right_side, right_side)
            .extrude(right_height)
        )
    
        # --- Step 3: Left square, connected to left edge of rectangle ---
        # Rectangle left edge at x=-30. Left square side=10, centered in Y.
        # Square spans x: -40..-30, y: -5..5, z: 0..5
        # Center of left square: x = -30 - 10/2 = -35, y = 0
        left_sq = (
            cq.Workplane("XY")
            .center(-(rect_length/2 + left_side/2), 0)
            .rect(left_side, left_side)
            .extrude(left_height)
        )
    
        # --- Step 4: Union all three parts ---
        result = base.union(right_sq).union(left_sq)
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        # X: from -40 (left square left edge) to +50 (right square right edge) → xlen=90
        expected_xlen = rect_length/2 + right_side + rect_length/2 + left_side  # 30+20+30+10=90
        assert abs(bb.xlen - expected_xlen) < TOL, f"X length: expected {expected_xlen}, got {bb.xlen}"
    
        # Y: max of all widths. Rectangle width=20, right square=20, left square=10 → ylen=20
        expected_ylen = max(rect_width, right_side, left_side)
        assert abs(bb.ylen - expected_ylen) < TOL, f"Y length: expected {expected_ylen}, got {bb.ylen}"
    
        # Z: max of all heights → 10 (right square)
        expected_zlen = max(rect_height, right_height, left_height)
        assert abs(bb.zlen - expected_zlen) < TOL, f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # X extents
        assert abs(bb.xmin - (-(rect_length/2 + left_side))) < TOL, f"xmin: expected {-(rect_length/2+left_side)}, got {bb.xmin}"
        assert abs(bb.xmax - (rect_length/2 + right_side)) < TOL, f"xmax: expected {rect_length/2+right_side}, got {bb.xmax}"
    
        # Volume check
        vol_rect  = rect_length  * rect_width  * rect_height   # 60*20*5 = 6000
        vol_right = right_side   * right_side  * right_height  # 20*20*10 = 4000
        vol_left  = left_side    * left_side   * left_height   # 10*10*5  = 500
        expected_vol = vol_rect + vol_right + vol_left          # 10500
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Rectangle length ≈ 3× width
        assert abs(rect_length / rect_width - 3.0) < TOL, \
            f"Rectangle length/width ratio: expected 3.0, got {rect_length/rect_width}"
    
        # Left square area = 25% of right square area
        left_area  = left_side  ** 2   # 100
        right_area = right_side ** 2   # 400
        assert abs(left_area / right_area - 0.25) < TOL, \
            f"Left/right area ratio: expected 0.25, got {left_area/right_area}"
    
        # Both square areas smaller than rectangle top face area
        rect_area = rect_length * rect_width  # 1200
        assert left_area  < rect_area, f"Left square area {left_area} should be < rect area {rect_area}"
        assert right_area < rect_area, f"Right square area {right_area} should be < rect area {rect_area}"
    
        # Right square extruded 2× left square
        assert abs(right_height / left_height - 2.0) < TOL, \
            f"Right/left height ratio: expected 2.0, got {right_height/left_height}"
    
        # Connectivity: check that the union produced a single solid (no gaps)
        num_solids = result.solids().size()
        assert num_solids == 1, f"Expected 1 solid (all connected), got {num_solids}"
    
        # Center of mass should be shifted toward the right (heavier right square)
        com = cq.Shape.centerOfMass(result.val())
        assert com.x > 0, f"Center of mass X should be positive (right-heavy), got {com.x}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: x={bb.xlen}, y={bb.ylen}, z={bb.zlen}")
        print(f"Volume: {actual_vol:.1f} (expected {expected_vol:.1f})")
        print(f"Center of mass: ({com.x:.2f}, {com.y:.2f}, {com.z:.2f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00009529/gpt_generated.stl')
