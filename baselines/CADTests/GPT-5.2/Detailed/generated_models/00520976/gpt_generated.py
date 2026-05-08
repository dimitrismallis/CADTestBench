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
        base_xy = 0.75
        base_h = 0.25
    
        cut_xy = 0.15          # ~1/5 of 0.75
        cut_depth = 0.5        # negative extrude depth (cut downward)
    
        # Base solid (centered on origin)
        result = cq.Workplane("XY").box(base_xy, base_xy, base_h, centered=True)
    
        # Place cut square on top face, positioned so top-right corners touch.
        # Base top-right corner in local top-face coordinates is (base_xy/2, base_xy/2).
        # For a centered cut square, its top-right corner is at (cut_xy/2, cut_xy/2) from its center.
        # Therefore, cut square center should be at:
        # (base_xy/2 - cut_xy/2, base_xy/2 - cut_xy/2)
        cx = base_xy / 2 - cut_xy / 2
        cy = base_xy / 2 - cut_xy / 2
    
        result = (
            result
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(cx, cy)
            .rect(cut_xy, cut_xy)
            .cutBlind(-cut_depth)  # cut downward from the top face
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00520976/gpt_generated.stl')
