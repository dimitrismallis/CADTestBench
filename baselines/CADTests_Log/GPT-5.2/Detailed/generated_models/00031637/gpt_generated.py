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
        L = 1.05964
        W = 0.56859
        H = 0.26362
    
        cut_L = L / 4.0                 # 0.26491 (note: prompt's ~0.206758 seems inconsistent with 1/4 of L)
        cut_W = W                       # same as original width
        cut_H = H * 3.0 / 4.0           # 0.197715
    
        # Main solid (centered at origin)
        main = cq.Workplane("XY").box(L, W, H, centered=True)
    
        # Cut-out box: flush to the right side of the main box
        # Main right face is at x = +L/2. Cut-out right face should match that:
        # cut center x = (L/2) - (cut_L/2)
        cut_center_x = (L / 2.0) - (cut_L / 2.0)
    
        cutout = (
            cq.Workplane("XY")
            .center(cut_center_x, 0)
            .box(cut_L, cut_W, cut_H, centered=True)
        )
    
        result = main.cut(cutout)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00031637/gpt_generated.stl')
