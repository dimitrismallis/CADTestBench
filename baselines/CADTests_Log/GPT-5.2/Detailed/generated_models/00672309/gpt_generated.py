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
        h = 0.6
        cyl_d = 1.498046
        cyl_r = cyl_d / 2.0
    
        hole_d = 0.748126
    
        chan_len = 0.188827                 # along X (radial/outward)
        chan_w = cyl_d / 2.0                # along Y
        pad = 0.142454                      # gap from cylinder outer surface
    
        # --- Base cylinder ---
        part = cq.Workplane("XY").cylinder(h, cyl_r)
    
        # --- Through hole ---
        part = part.faces(">Z").workplane(centerOption="CenterOfMass").hole(hole_d)
    
        # --- Rectangular channel attached on outer edge (+X side) ---
        # Place a box whose inner face is offset from the cylinder surface by 'pad'
        # Cylinder spans X in [-cyl_r, +cyl_r]. Inner face of channel at x = cyl_r + pad.
        # Box is centered at x = (inner_face + chan_len/2).
        chan_center_x = cyl_r + pad + chan_len / 2.0
    
        channel = (
            cq.Workplane("XY")
            .center(chan_center_x, 0)
            .box(chan_len, chan_w, h, centered=True)
        )
    
        part = part.union(channel)
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00672309/gpt_generated.stl')
