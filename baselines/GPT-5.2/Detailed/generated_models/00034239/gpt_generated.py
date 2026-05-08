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
        L = 1.5      # length (X)
        W = 1.2      # width  (Y)
        H = 0.15     # height (Z)
    
        d_big = 0.675
        d_small = 0.1968
        edge_clear = 0.033  # distance from rectangle edge to hole edge
    
        r_small = d_small / 2.0
    
        # Small hole center positions: keep hole edge 'edge_clear' from left/right edges
        x_left_center  = -L/2.0 + edge_clear + r_small
        x_right_center =  L/2.0 - edge_clear - r_small
        y_center = 0.0
    
        # Base block
        part = cq.Workplane("XY").box(L, W, H, centered=True)
    
        # Cut holes through all
        part = (
            part.faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints([(0.0, 0.0), (x_left_center, y_center), (x_right_center, y_center)])
            .hole(d_big)  # first point uses d_big? No: hole() applies to all points.
        )
    
        # Since hole() uses one diameter for all points, cut in two steps:
        part = (
            cq.Workplane("XY").box(L, W, H, centered=True)
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .hole(d_big)  # central hole at origin
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints([(x_left_center, y_center), (x_right_center, y_center)])
            .hole(d_small)
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00034239/gpt_generated.stl')
