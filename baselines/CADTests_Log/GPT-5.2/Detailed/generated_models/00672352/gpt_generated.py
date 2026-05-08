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
        length = 0.75
        width = 0.375
        height = 0.015611
    
        hole_d = 0.09375
        pad = 0.015625
    
        # Base solid (centered on origin)
        part = cq.Workplane("XY").box(length, width, height, centered=True)
    
        # Hole location relative to centered box:
        # top-right corner is at (+length/2, +width/2) in XY
        hole_x = length / 2 - pad
        hole_y = width / 2 - pad
    
        part = (
            part
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .pushPoints([(hole_x, hole_y)])
            .hole(hole_d)
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00672352/gpt_generated.stl')
