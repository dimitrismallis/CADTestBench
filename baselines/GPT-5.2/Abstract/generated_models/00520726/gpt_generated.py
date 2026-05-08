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
        side = 16.0                 # square side length
        body_h = 1.9 * side         # "almost twice" the side length
        wall = side * 0.12          # wall thickness for hollowing
        stud_d = side * 0.55        # typical-ish stud diameter relative to body
        stud_h = body_h / 7.0       # about 1/7th of the body height
    
        # --- Main body: elongated square prism ---
        body = cq.Workplane("XY").rect(side, side).extrude(body_h)
    
        # --- Hollow out, keeping the top (open bottom) ---
        # shell() removes the selected face(s) then offsets inward by -wall
        body = body.faces("<Z").shell(-wall)
    
        # --- Top stud ---
        stud = (
            body.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .circle(stud_d / 2.0)
            .extrude(stud_h)
        )
    
        return stud
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00520726/gpt_generated.stl')
