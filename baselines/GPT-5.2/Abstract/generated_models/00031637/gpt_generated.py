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
        length = 120.0
        width  = 30.0
        height = 20.0
    
        cut_len = length / 4.0
        cut_wid = width
        cut_hgt = height * 3.0 / 4.0
    
        # --- Base solid (centered at origin) ---
        base = cq.Workplane("XY").box(length, width, height, centered=True)
    
        # --- Cutout block positioned on the right side (+X) ---
        # Base box spans X: [-L/2, +L/2], Y: [-W/2, +W/2], Z: [-H/2, +H/2]
        # Cutout should remove from right side, full width, and from bottom up to 3/4 height.
        cutout = (
            cq.Workplane("XY")
            .box(cut_len, cut_wid, cut_hgt, centered=True)
            .translate((
                length/2.0 - cut_len/2.0,   # align to right face
                0.0,                        # same width, centered in Y
                -height/2.0 + cut_hgt/2.0   # sit on bottom face
            ))
        )
    
        result = base.cut(cutout)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00031637/gpt_generated.stl')
