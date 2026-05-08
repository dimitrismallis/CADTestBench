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
        # Parameters
        thickness = 12.0
    
        # "Pentagon-like" outline with the top-left and top-right edges each split into two
        # segments with a very shallow kink (obtuse angle close to 180°).
        #
        # Points are in CCW order. The "kink" points (p2 and p4) are almost collinear
        # with their neighboring points to create the near-180° obtuse angle.
        p0 = (-30.0, -20.0)  # bottom-left
        p1 = ( 30.0, -20.0)  # bottom-right
        p2 = ( 22.0,  18.0)  # right upper shoulder
        p3 = (  0.0,  30.0)  # top apex
        p4 = (-22.0,  18.0)  # left upper shoulder
    
        # Kink points along the top edges (very small deviation from straight line)
        # Edge p2->p3 is split into p2->kR->p3, and p3->p4 into p3->kL->p4.
        kR = ( 11.0,  24.2)  # near the line from p2 to p3, slight offset
        kL = (-11.0,  24.2)  # near the line from p3 to p4, slight offset
    
        pts = [p0, p1, p2, kR, p3, kL, p4]
    
        result = (
            cq.Workplane("XY")
            .moveTo(*pts[0])
            .lineTo(*pts[1])
            .lineTo(*pts[2])
            .lineTo(*pts[3])  # split top-right edge (near-straight obtuse kink)
            .lineTo(*pts[4])
            .lineTo(*pts[5])  # split top-left edge (near-straight obtuse kink)
            .lineTo(*pts[6])
            .close()
            .extrude(thickness)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00039777/gpt_generated.stl')
