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
        L = 200.0   # overall length (X) - "very long"
        W = 40.0    # overall width  (Y)
        T = 6.0     # slight extrusion thickness (Z)
    
        cut_L = L / 4.0   # about 1/4th the length of the original
        cut_W = W * 0.45  # modest cut width
        margin_x = 8.0
        margin_y = 6.0
    
        # Center position of cutout toward bottom-right of the plate
        cut_cx = (L / 2.0) - margin_x - (cut_L / 2.0)   # near +X edge
        cut_cy = (-W / 2.0) + margin_y + (cut_W / 2.0)  # near -Y edge
    
        # --- Model ---
        base = cq.Workplane("XY").rect(L, W).extrude(T)
    
        result = (
            base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(cut_cx, cut_cy)
            .rect(cut_L, cut_W)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00997068/gpt_generated.stl')
