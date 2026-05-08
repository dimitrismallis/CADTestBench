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
        # --- Parameters (mm) ---
        length = 120.0
        width = 30.0
        thickness = 4.0
    
        hole_d = 4.0
        tri_side = 20.0  # spacing for the triangular hole pattern
    
        # Triangle points (equilateral-ish) centered on the plate
        # Two bottom points and one top point
        h = (math.sqrt(3) / 2.0) * tri_side
        pts = [
            (-tri_side / 2.0, -h / 3.0),
            ( tri_side / 2.0, -h / 3.0),
            (0.0,             2.0 * h / 3.0),
        ]
    
        plate = cq.Workplane("XY").rect(length, width).extrude(thickness)
    
        result = (
            plate
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints(pts)
            .hole(hole_d)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00996473/gpt_generated.stl')
