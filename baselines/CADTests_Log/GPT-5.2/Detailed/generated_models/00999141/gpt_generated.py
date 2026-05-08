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
        bottom_len = 0.628103
        top_len    = 0.240157
        height     = 0.722001
        top_shift  = 0.009237   # top edge center shifted right from bottom center
        thickness  = 0.011084
        final_shift_left = 0.018474
    
        # --- Derived coordinates (XY sketch, Z extrusion) ---
        # Bottom edge centered at x=0 on y=0
        x_bl = -bottom_len / 2.0
        x_br =  bottom_len / 2.0
        y_b  = 0.0
    
        # Top edge centered at x=top_shift on y=height
        x_tl = top_shift - top_len / 2.0
        x_tr = top_shift + top_len / 2.0
        y_t  = height
    
        # --- Sketch trapezium and extrude ---
        plate = (
            cq.Workplane("XY")
            .moveTo(x_bl, y_b)
            .lineTo(x_br, y_b)
            .lineTo(x_tr, y_t)
            .lineTo(x_tl, y_t)
            .close()
            .extrude(thickness)
            .translate((-final_shift_left, 0, 0))
        )
    
        return plate
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00999141/gpt_generated.stl')
