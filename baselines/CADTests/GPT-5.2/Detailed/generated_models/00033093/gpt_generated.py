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
        L = 1.16102   # length (X)
        W = 0.0729    # width  (Y)
        H = 1.5       # height (Z)
    
        hole_d = 0.072899
    
        # Hole placement from edges (along X)
        left_from_left = 0.252909
        right_from_right = 0.127776
    
        # Hole depth: distance from top face downwards
        hole_depth = 0.595655
    
        # Slight offset from centerline (along Y), symmetric
        y_off = W * 0.25  # "slightly" offset; keeps holes inside the narrow width
    
        # Convert edge-based X positions to coordinates on a centered workplane
        x_left = -L / 2 + left_from_left
        x_right = L / 2 - right_from_right
    
        plate = cq.Workplane("XY").box(L, W, H, centered=(True, True, False))
    
        # Drill two blind holes from the top face, parallel (both along Z)
        result = (
            plate
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints([(x_left, -y_off), (x_right, y_off)])
            .hole(hole_d, depth=hole_depth)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00033093/gpt_generated.stl')
