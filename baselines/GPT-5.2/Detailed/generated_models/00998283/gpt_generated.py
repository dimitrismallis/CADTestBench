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
        base_len = 0.3
        top_len = 0.225
        trap_h = 0.1875
        extrude_len = 0.75
    
        # Center the trapezoid about the origin:
        # Put bottom base at y = -trap_h/2 and top base at y = +trap_h/2
        yb = -trap_h / 2.0
        yt =  trap_h / 2.0
        xb = base_len / 2.0
        xt = top_len / 2.0
    
        pts = [
            (-xb, yb),  # bottom-left
            ( xb, yb),  # bottom-right
            ( xt, yt),  # top-right
            (-xt, yt),  # top-left
        ]
    
        result = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(extrude_len)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00998283/gpt_generated.stl')
