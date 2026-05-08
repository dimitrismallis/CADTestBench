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
        cyl_d = 0.95
        cyl_r = cyl_d / 2.0
        cyl_h = 0.475
    
        rect_w = 0.76
        rect_l = 0.7
        boss_h = 0.2375  # about half the cylinder height
    
        # Base cylinder
        result = cq.Workplane("XY").circle(cyl_r).extrude(cyl_h)
    
        # Rectangular boss on top face, centered
        result = (
            result
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(rect_w, rect_l, centered=True)
            .extrude(boss_h)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00672355/gpt_generated.stl')
