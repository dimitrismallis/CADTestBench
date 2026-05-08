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
        # --- Parameters (mm) ---
        cyl_d = 50.0
        cyl_r = cyl_d / 2.0
        cyl_h = 30.0
    
        rect_w = 0.8 * cyl_d                 # ~4/5 diameter
        rect_h = 0.1 * rect_w                # ~1/10 of rectangle width
        rect_extrude = 0.5 * cyl_h           # ~half cylinder height
    
        # --- Model ---
        result = (
            cq.Workplane("XY")
            .circle(cyl_r)
            .extrude(cyl_h)                  # cylinder from Z=0 to Z=cyl_h
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .rect(rect_w, rect_h, centered=True)
            .extrude(rect_extrude)           # raised rectangular feature
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00672355/gpt_generated.stl')
