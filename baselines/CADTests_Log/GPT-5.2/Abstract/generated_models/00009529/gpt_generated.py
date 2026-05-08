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
        rect_w = 30.0
        rect_l = 3.0 * rect_w
        rect_h = 10.0
    
        # Right square (larger)
        sq_r_side = 20.0
        sq_r_h = 12.0
    
        # Left square: 75% smaller area than right => area_left = 0.25 * area_right
        # side scales with sqrt(area) => side_left = 0.5 * side_right
        sq_l_side = 0.5 * sq_r_side
        sq_l_h = 0.5 * sq_r_h  # larger square extruded twice the smaller
    
        # --- Base rectangle (centered) ---
        base = cq.Workplane("XY").rect(rect_l, rect_w).extrude(rect_h)
    
        # --- Add right square, attached to +X edge of rectangle ---
        right_sq = (
            cq.Workplane("XY")
            .center(rect_l / 2 + sq_r_side / 2, 0)
            .rect(sq_r_side, sq_r_side)
            .extrude(sq_r_h)
        )
    
        # --- Add left square, attached to -X edge of rectangle ---
        left_sq = (
            cq.Workplane("XY")
            .center(-(rect_l / 2 + sq_l_side / 2), 0)
            .rect(sq_l_side, sq_l_side)
            .extrude(sq_l_h)
        )
    
        result = base.union(right_sq).union(left_sq)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00009529/gpt_generated.stl')
