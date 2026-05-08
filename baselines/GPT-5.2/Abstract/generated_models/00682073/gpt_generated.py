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
        # --- Parameters (mm) ---
        base_L = 90.0   # larger side of base rectangle (X direction)
        base_W = 45.0   # smaller side of base rectangle (Y direction)
        base_H = 20.0   # extrusion height (Z)
    
        cut_L = (2.0 / 3.0) * base_L   # larger side ~2/3 of base larger side
        cut_W = 0.70 * base_W          # choose a reasonable width to form "U" legs
        cut_depth = base_H             # cut all the way through (can be reduced if desired)
    
        # Place cut rectangle centered in X, and touching the +Y (top) edge of the base
        cut_center_y = (base_W / 2.0) - (cut_W / 2.0)
    
        # --- Model ---
        result = (
            cq.Workplane("XY")
            .rect(base_L, base_W)
            .extrude(base_H)
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .center(0, cut_center_y)
            .rect(cut_L, cut_W)
            .cutBlind(-cut_depth)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00682073/gpt_generated.stl')
