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
        length = 0.21429
        width = 0.75
        height = 0.21429
    
        hole_d = 0.05371
        edge_to_center_pad = 0.048699  # from each end edge (along length) to hole center
    
        # Hole center positions along the length (X axis), symmetric about origin
        x_off = (length / 2.0) - edge_to_center_pad
        hole_pts = [(-x_off, 0.0), (x_off, 0.0)]
    
        # Base solid
        part = cq.Workplane("XY").box(length, width, height, centered=True)
    
        # Through holes from top face
        part = (
            part.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .pushPoints(hole_pts)
            .hole(hole_d)
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00033624/gpt_generated.stl')
