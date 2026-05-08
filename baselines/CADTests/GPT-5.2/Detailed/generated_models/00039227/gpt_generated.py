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
        cyl_d = 1.27949
        cyl_r = cyl_d / 2.0
        cyl_h = 1.0  # not specified; choose a reasonable height
    
        rect_len = 0.787604
        rect_wid = 0.506095
    
        # Base cylinder
        result = cq.Workplane("XY").cylinder(cyl_h, cyl_r)
    
        # Centered rectangular cut through the cylinder (empty rectangle)
        result = (
            result
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(rect_len, rect_wid)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00039227/gpt_generated.stl')
