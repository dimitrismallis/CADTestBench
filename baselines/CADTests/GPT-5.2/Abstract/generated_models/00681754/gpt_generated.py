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
        rect_len = 80.0
        rect_wid = 40.0
        rect_h   = 20.0
    
        cyl_d = rect_len / 4.0   # per request: ~1/4 of rectangle length
        cyl_h = 25.0
    
        result = (
            cq.Workplane("XY")
            # Base block: sketch rectangle then extrude
            .rect(rect_len, rect_wid)
            .extrude(rect_h)
            # Cylinder on top: sketch circle at center of top face then extrude up
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .circle(cyl_d / 2.0)
            .extrude(cyl_h)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00681754/gpt_generated.stl')
