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
        length = 80.0   # X direction
        width  = 40.0   # Y direction
        thick  = 8.0    # Z direction
    
        hole_d = 16.0
        hole_offset_x = -8.0  # negative X = closer to left side than right
    
        plate = (
            cq.Workplane("XY")
            .rect(length, width)
            .extrude(thick)
        )
    
        result = (
            plate
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(hole_offset_x, 0)
            .hole(hole_d)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00670231/gpt_generated.stl')
