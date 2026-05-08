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
        semi_d = 40.0                 # diameter of the bottom semicircle
        semi_r = semi_d / 2.0
        rect_w = semi_d               # rectangle width matches semicircle diameter
        rect_h = 50.0                 # rectangle height above the semicircle
        thickness = 6.0               # extrusion height
    
        hole_d = semi_d / 4.0         # 1/4th size diameter of the semicircle
        hole_center = (0.0, -rect_h / 2.0)  # center of the semicircle in the 2D sketch
    
        # --- 2D profile: rectangle + circle (circle provides the bottom semicircle) ---
        profile = (
            cq.Workplane("XY")
            .rect(rect_w, rect_h)
            .circle(semi_r)  # centered at origin; overlaps rectangle to form a "tag" outline
            .combine()
        )
    
        # --- Extrude and cut hole at semicircle center ---
        tag = profile.extrude(thickness)
    
        tag = (
            tag.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .pushPoints([hole_center])
            .hole(hole_d)
        )
    
        return tag
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00031303/gpt_generated.stl')
