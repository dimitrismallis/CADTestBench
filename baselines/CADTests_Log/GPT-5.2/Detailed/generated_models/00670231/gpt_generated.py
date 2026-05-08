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
        length = 0.9   # X
        width  = 1.5   # Y
        height = 0.75  # Z
    
        hole_d = 0.45
        x_offset_left = -0.075  # toward left side (negative X)
    
        part = (
            cq.Workplane("XY")
            .box(length, width, height, centered=True)
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(x_offset_left, 0)
            .hole(hole_d)
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00670231/gpt_generated.stl')
