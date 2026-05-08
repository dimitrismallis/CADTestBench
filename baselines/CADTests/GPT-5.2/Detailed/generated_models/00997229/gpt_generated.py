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
        L = 0.848067
        W = 0.197368
    
        d_small = 0.157782
        d_large = 0.196626
        hole_d = 0.094737
    
        thickness = 0.05  # extrusion thickness (not specified in prompt)
    
        r_small = d_small / 2.0
        r_large = d_large / 2.0
    
        x_left = -L / 2.0
        x_right = L / 2.0
    
        # Build 2D outline as a union of a rectangle and two circles
        sk = (
            cq.Sketch()
            .rect(L, W)  # base handle rectangle
            .circle(r_small, mode="a").moved(x_left, 0)  # add small end circle
            .circle(r_large, mode="a").moved(x_right, 0)  # add large end circle
        )
    
        body = cq.Workplane("XY").placeSketch(sk).extrude(thickness)
    
        # Cut holes through both ends
        body = (
            body.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .pushPoints([(x_left, 0.0), (x_right, 0.0)])
            .hole(hole_d)
        )
    
        return body
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00997229/gpt_generated.stl')
