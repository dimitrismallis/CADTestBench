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
        outer_d = 30.0
        inner_d = 20.0
        height  = 6.0
        fillet_r = 0.5
    
        if inner_d >= outer_d:
            raise ValueError("inner_d must be smaller than outer_d")
        if fillet_r <= 0:
            raise ValueError("fillet_r must be > 0")
    
        outer_r = outer_d / 2.0
        inner_r = inner_d / 2.0
    
        ring = (
            cq.Workplane("XY")
            .circle(outer_r)
            .circle(inner_r)
            .extrude(height)
        )
    
        # Fillet the top and bottom circular edges (more reliable than "|Z" here)
        ring = (
            ring
            .faces("+Z or -Z")
            .edges()
            .fillet(fillet_r)
        )
    
        return ring
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00005358/gpt_generated.stl')
