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
        # Parameters (units as given in prompt)
        L = 0.647727
        W = 0.051136
        H = 0.025568
    
        pad_len = L / 16.0
        pad_w = W
        pad_h = H / 3.0
    
        # Base solid (centered at origin)
        base = cq.Workplane("XY").box(L, W, H, centered=True)
    
        # Pads on the top face, centered on the short edges (x-min and x-max ends)
        x_off = (L / 2.0) - (pad_len / 2.0)
    
        pads = (
            base.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .pushPoints([(-x_off, 0.0), (x_off, 0.0)])
            .rect(pad_len, pad_w)
            .extrude(pad_h, combine=True)
        )
    
        return pads
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00672272/gpt_generated.stl')
