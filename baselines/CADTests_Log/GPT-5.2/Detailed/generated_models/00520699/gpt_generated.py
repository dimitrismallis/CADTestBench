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
        bulb_d = 0.15
        bulb_r = bulb_d / 2.0
        bulb_h = 0.0375
    
        stem_len = 0.691425
        stem_w   = 0.093715
        stem_h   = 0.02625  # slightly less than bulb height
    
        # --- Bulb (small cylinder) ---
        bulb = cq.Workplane("XY").circle(bulb_r).extrude(bulb_h)
    
        # --- Stem (very long rectangle extruded slightly less than cylinder) ---
        # Place as a box with its bottom on Z=0, and its near end tangent to the bulb at y=+bulb_r.
        # Box is created centered by default, so we translate by half-length/width/height.
        stem = (
            cq.Workplane("XY")
            .box(stem_len, stem_w, stem_h, centered=True)
            .translate((stem_len / 2.0, bulb_r + stem_w / 2.0, stem_h / 2.0))
        )
    
        # --- Combine ---
        asm = bulb.union(stem)
    
        # --- Rotate for "proper orientation" (make the long stem point upward along +Z) ---
        # Rotate about X axis: +90° maps +Y to +Z.
        asm = asm.rotate((0, 0, 0), (1, 0, 0), 90)
    
        return asm
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00520699/gpt_generated.stl')
