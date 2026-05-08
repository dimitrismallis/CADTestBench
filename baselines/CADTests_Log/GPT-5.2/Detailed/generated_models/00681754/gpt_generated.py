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
        length = 1.09115
        width = 1.5
        height = 0.361568
    
        cyl_diam = 0.427203
        cyl_height = 0.271176
    
        # Base block from a rectangle sketch, extruded upward
        base = (
            cq.Workplane("XY")
            .rect(length, width)
            .extrude(height)
        )
    
        # Cylinder on top face, centered
        result = (
            base
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .circle(cyl_diam / 2.0)
            .extrude(cyl_height)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00681754/gpt_generated.stl')
