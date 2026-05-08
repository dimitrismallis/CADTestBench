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
        L = 1.5
        W = 0.017559
        H = 0.546823
    
        hole_d = 0.301003
        hole_r = hole_d / 2.0
    
        x_from_left = 0.446488
        y_from_top = 0.050167
        extra_spacing = 0.050167
        pitch = hole_d + extra_spacing  # center-to-center spacing along length
    
        # Convert edge-based offsets to coordinates on a centered top workplane:
        # Left edge is at x = -L/2, top edge is at y = +W/2
        x0 = -L / 2.0 + x_from_left
        y0 = +W / 2.0 - y_from_top
    
        pts = [(x0 + i * pitch, y0) for i in range(3)]
    
        # --- Model ---
        part = (
            cq.Workplane("XY")
            .box(L, W, H, centered=True)
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints(pts)
            .hole(hole_d)  # through-hole
            .rotate((0, 0, 0), (0, 0, 1), 180)
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00984033/gpt_generated.stl')
