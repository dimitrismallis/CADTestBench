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
        L = 0.333333
        W = 0.066667
        H_rect = 0.083333
    
        r_cyl = 0.022222
        H_cyl = 0.666667
    
        # Place cylinder near one side edge on the top face
        edge_margin = 0.001  # "very close to the edge"
        y_pos = (W / 2.0) - r_cyl - edge_margin  # near +Y edge, still fully on the top face
    
        base = cq.Workplane("XY").box(L, W, H_rect, centered=True)
    
        result = (
            base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(0, y_pos)
            .circle(r_cyl)
            .extrude(H_cyl, combine=True)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00009998/gpt_generated.stl')
