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
        cyl_radius = 20.0
        cyl_height = 30.0
    
        rect_width = 12.0   # X size of rectangular void
        rect_length = 18.0  # Y size of rectangular void
    
        # Base cylinder
        result = cq.Workplane("XY").cylinder(cyl_height, cyl_radius)
    
        # Cut an empty rectangle through the center
        result = (
            result
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(rect_width, rect_length)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00039227/gpt_generated.stl')
