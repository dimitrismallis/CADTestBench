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
        # Parameters (units as given)
        base_len = 1.49593
        top_len = 0.910569
        trap_h = 0.382114
        x_shift = 0.026423
        width = 0.589754  # total prism thickness
    
        # Center trapezoid vertically about Y=0: bottom at -h/2, top at +h/2
        yb = -trap_h / 2.0
        yt =  trap_h / 2.0
    
        xb0, xb1 = -base_len / 2.0, base_len / 2.0
        xt0, xt1 = -top_len / 2.0,  top_len / 2.0
    
        pts = [
            (xb0 + x_shift, yb),
            (xb1 + x_shift, yb),
            (xt1 + x_shift, yt),
            (xt0 + x_shift, yt),
        ]
    
        result = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            # Extrude symmetrically about the sketch plane (total thickness = width)
            .extrude(width / 2.0, both=True)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00675952/gpt_generated.stl')
