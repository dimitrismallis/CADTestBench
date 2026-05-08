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
        # --- Inputs (units as provided) ---
        pts = [
            (0.0, 0.07722659),
            (0.01489577, 0.03904715),
            (0.07129721, 0.03904715),
            (0.01778815, 0.01070181),
            (0.05105054, -0.0378901),
            (0.0, -0.0083879),
            (-0.0539429, -0.03470857),
            (-0.02183747, 0.006074),
            (-0.07071871, 0.02429601),
            (-0.01865585, 0.036444),
            (0.0, 0.0772265),
        ]
        height = 0.0634998086654784
        scale_factor = 9.711714302145034
    
        # --- Build star sketch and extrude ---
        star = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .wire()
            .toPending()
            .extrude(height)
        )
    
        # --- Uniform scale of the entire solid ---
        scaled = star.val().scale(scale_factor)
    
        return cq.Workplane("XY").newObject([scaled])
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00681589/gpt_generated.stl')
