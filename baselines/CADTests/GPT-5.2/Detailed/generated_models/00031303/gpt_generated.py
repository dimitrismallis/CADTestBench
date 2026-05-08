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
        # --- Parameters (units as given) ---
        rect_len = 0.75   # X size
        rect_wid = 0.75   # Y size
        semi_d   = 0.75
        semi_r   = semi_d / 2.0
    
        height = 0.16071
        hole_d = 0.267857
    
        # Rectangle centered at origin; bottom edge at y = -rect_wid/2
        rect_bottom_y = -rect_wid / 2.0
        semi_center_x, semi_center_y = 0.0, rect_bottom_y
    
        # Build a single face from two overlapping closed wires (rect + circle),
        # then extrude. The circle overlaps the rectangle so the union is a "U/tag" outline.
        tag = (
            cq.Workplane("XY")
            .rect(rect_len, rect_wid)
            .moveTo(semi_center_x, semi_center_y).circle(semi_r)
            .combine()                 # merge the two wires into one face
            .extrude(height)
        )
    
        # Cut the circular hole at the semicircle center through the full thickness
        tag = (
            tag.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .center(semi_center_x, semi_center_y)
            .hole(hole_d, depth=height)
        )
    
        return tag
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00031303/gpt_generated.stl')
