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
        square_size = 40.0     # side length
        thickness = 3.0        # slight extrusion
        hole_d = 1.0           # very small hole
    
        result = (
            cq.Workplane("XY")
            .rect(square_size, square_size)
            .extrude(thickness)
            .faces(">Z").workplane()
            .hole(hole_d)  # centered by default on the workplane origin
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00672804/gpt_generated.stl')
