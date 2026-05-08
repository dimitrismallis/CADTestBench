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
        # Parameters (units as provided)
        length = 0.74999
        width  = 0.73843
        height = 0.11078
        fillet_r = 0.038
    
        # Safety clamp: fillet radius cannot exceed half the smallest relevant thickness
        max_r = 0.5 * min(length, width, height)
        r = min(fillet_r, max_r * 0.999)
    
        result = (
            cq.Workplane("XY")
            .box(length, width, height, centered=True)
            # Fillet all edges of the solid
            .edges()
            .fillet(r)
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00521969/gpt_generated.stl')
