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
        # Convert meters to millimeters (CadQuery default units)
        outer_w = 0.06 * 1000.0   # 60 mm
        outer_l = 0.06 * 1000.0   # 60 mm
        height  = 0.75 * 1000.0   # 750 mm
        pad     = 0.0045 * 1000.0 # 4.5 mm wall thickness on each side
    
        inner_w = outer_w - 2 * pad
        inner_l = outer_l - 2 * pad
        if inner_w <= 0 or inner_l <= 0:
            raise ValueError("Padding is too large; inner dimensions became non-positive.")
    
        tube = (
            cq.Workplane("XY")
            .rect(outer_l, outer_w)
            .extrude(height)
            .faces(">Z").workplane()
            .rect(inner_l, inner_w)
            .cutThruAll()
        )
    
        return tube
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00670259/gpt_generated.stl')
