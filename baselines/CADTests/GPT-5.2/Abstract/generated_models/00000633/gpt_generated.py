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
        thickness = 6.0
        hole_diameter = 12.0
    
        result = (
            cq.Workplane("XY")
            .box(length, width, thickness, centered=(True, True, False))  # bottom at Z=0
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .hole(hole_diameter)  # through-hole
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00000633/gpt_generated.stl')
