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
        L = 1.0
        W = 0.1
        H = 1.25
    
        hole_L = 0.5
        hole_W = 0.1
        hole_H = 0.075
        bottom_padding = 0.25
    
        # --- Main solid: base at Z=0, centered in X/Y ---
        body = cq.Workplane("XY").box(L, W, H, centered=(True, True, False))
    
        # --- Rectangular hole (a pocket) ---
        # Place a workplane at the Z height where the pocket starts, then cut upward by hole_H.
        body = (
            body
            .faces("<Z").workplane(offset=bottom_padding)
            .rect(hole_L, hole_W)
            .cutBlind(hole_H)
        )
    
        # --- Slight translation for visualization ---
        result = body.translate((0.2, 0.2, 0.0))
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00521025/gpt_generated.stl')
