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
        # Units as given in prompt (CadQuery default is mm, but we treat these as "units")
        L = 0.9375     # base length (X)
        W = 1.5        # base width  (Y)
        H = 0.375      # base height (Z)
    
        arm_len = 0.234375   # short arm length (in X from corner)
        arm_h   = 0.328125   # arm thickness/height in Y from corner (forms the "L" width)
    
        # Choose an L-block extrusion height (not specified explicitly)
        l_extrude = 0.328125
    
        # Base block centered at origin by default
        base = cq.Workplane("XY").box(L, W, H, centered=True)
    
        # Create L-shaped profile on top face, aligned to a corner.
        # We'll anchor at the top face's (-X, -Y) corner by shifting the workplane origin there.
        # L-shape is union of:
        #  - a long bar along X: length L, thickness arm_h in Y
        #  - a short bar along Y: thickness arm_len in X, height arm_h in Y (same), but extended in Y
        # Here we implement as a single polyline "L" outline:
        # (0,0)->(L,0)->(L,arm_h)->(arm_len,arm_h)->(arm_len,W)->(0,W)->close
        l_block = (
            base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(-L/2, -W/2)  # move origin to the (-X,-Y) corner of the top face
            .moveTo(0, 0)
            .lineTo(L, 0)
            .lineTo(L, arm_h)
            .lineTo(arm_len, arm_h)
            .lineTo(arm_len, W)
            .lineTo(0, W)
            .close()
            .extrude(l_extrude, combine=True)
        )
    
        # Translate entire structure vertically by half the base height
        result = l_block.translate((0, 0, H/2))
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00998012/gpt_generated.stl')
