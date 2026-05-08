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
        # Parameters (mm)
        length = 80.0
        width = 50.0
        thickness = 5.0
    
        edge_margin = 6.0   # distance from each edge to hole center
        hole_d = 4.0
    
        plate = cq.Workplane("XY").box(length, width, thickness, centered=True)
    
        # Hole centers near corners: use an inset construction rectangle and select its vertices
        result = (
            plate
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(length - 2 * edge_margin, width - 2 * edge_margin, forConstruction=True)
            .vertices()
            .hole(hole_d)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00006578/gpt_generated.stl')
