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
        L = 0.5
        W = 0.5
        H = 0.633333
    
        cyl_h = 0.116667
        cyl_d = 0.316667
    
        cav_L = 0.411666
        cav_W = 0.411666
        cav_depth = 0.533333
        recess_from_bottom = 0.05  # cavity bottom is 0.05 above the outer bottom
    
        # Ensure cavity depth matches the recess requirement (leave a 0.05 floor)
        # If both are provided, prioritize the recess requirement for geometric consistency.
        cut_depth = min(cav_depth, H - recess_from_bottom)
    
        # Base block: centered in X/Y, bottom aligned to Z=0
        base = cq.Workplane("XY").box(L, W, H, centered=(True, True, False))
    
        # Top cylinder centered on top face
        with_cyl = (
            base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .circle(cyl_d / 2.0)
            .extrude(cyl_h)
        )
    
        # Bottom cavity: centered on bottom face, cut upward leaving 0.05 floor
        result = (
            with_cyl
            .faces("<Z").workplane(centerOption="CenterOfMass")
            .rect(cav_L, cav_W)
            .cutBlind(cut_depth)
        )
    
        # Base already aligned with ground plane (Z=0), so no translation needed.
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00520726/gpt_generated.stl')
