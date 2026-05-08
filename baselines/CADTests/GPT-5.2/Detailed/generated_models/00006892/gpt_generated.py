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
        L = 1.5
        W = 0.52105
        H = 0.15789
    
        # Semi-circle diameter per prompt: (half the length) + 2*0.067116
        semi_d = (L / 2.0) + 2.0 * 0.067116
        semi_r = semi_d / 2.0
    
        # --- Base solid (centered at origin) ---
        base = cq.Workplane("XY").box(L, W, H, centered=True)
    
        # --- Semicircle profile on one long face (+Y), cut through the prism ---
        # On the +Y face workplane: local X = global X, local Y = global Z.
        # Build a closed semicircle: arc from (-r,0) to (r,0) bulging to +Y, then close with chord.
        result = (
            base.faces(">Y")
            .workplane(centerOption="CenterOfMass")
            .moveTo(-semi_r, 0)
            .threePointArc((0, semi_r), (semi_r, 0))  # upper semicircle
            .lineTo(-semi_r, 0)
            .close()
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00006892/gpt_generated.stl')
