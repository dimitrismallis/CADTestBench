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
        length = 60.0
        width = 40.0
        thickness = 4.0  # marginal extrusion
    
        hole_d = 4.0
        edge_margin = 5.0  # distance from top/right edges
    
        # Base block from a rectangle sketch, then extrude
        part = (
            cq.Workplane("XY")
            .rect(length, width)
            .extrude(thickness)
        )
    
        # Hole on the top face, near the top-right corner (+X, +Y)
        part = (
            part
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .center(length / 2 - edge_margin, width / 2 - edge_margin)
            .hole(hole_d)
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00672352/gpt_generated.stl')
