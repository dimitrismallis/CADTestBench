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
        # --- Parameters (units as given) ---
        rect_L = 1.5
        rect_W = 0.55102
        rect_H = 0.08347
    
        sqR_S = 0.438776
        sqR_H = 0.280162
    
        sqL_S = 0.331633
        sqL_H = 0.127551
    
        # --- Base rectangle (centered on origin) ---
        base = cq.Workplane("XY").rect(rect_L, rect_W).extrude(rect_H)
    
        # --- Place squares so they touch the rectangle's left/right edges ---
        # Rectangle spans x in [-rect_L/2, +rect_L/2]
        # For a square of side S, to make it touch the right edge at x=+rect_L/2:
        # center_x = rect_L/2 + S/2 (so its left edge is at rect_L/2)
        x_right = rect_L / 2 + sqR_S / 2
        x_left  = -rect_L / 2 - sqL_S / 2
    
        right_sq = cq.Workplane("XY").center(x_right, 0).rect(sqR_S, sqR_S).extrude(sqR_H)
        left_sq  = cq.Workplane("XY").center(x_left, 0).rect(sqL_S, sqL_S).extrude(sqL_H)
    
        # Union all parts
        result = base.union(right_sq).union(left_sq)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00009529/gpt_generated.stl')
