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
        outer_len = 1.5
        outer_wid = 1.5
        padding = 0.17649
        height = 0.00265
    
        inner_len = outer_len - 2 * padding
        inner_wid = outer_wid - 2 * padding
        if inner_len <= 0 or inner_wid <= 0:
            raise ValueError("Padding too large: inner opening would be non-positive.")
    
        frame = (
            cq.Workplane("XY")
            .rect(outer_len, outer_wid)
            .rect(inner_len, inner_wid)   # second wire on same plane
            .extrude(height)              # extrudes as a face-with-hole => frame
        )
    
        return frame
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00038614/gpt_generated.stl')
