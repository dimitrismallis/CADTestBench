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
        W = 0.40625
        H = 0.023438
    
        hole_d = 0.046875
    
        side_pad  = 0.048699
        width_pad = 0.039062
        left_pad  = 0.242188
        right_pad = 0.242228
    
        # --- Base plate (centered on XY, symmetric about origin) ---
        plate = cq.Workplane("XY").box(L, W, H, centered=True)
    
        # --- Hole locations (on top face workplane) ---
        # Coordinate system: plate centered at (0,0); edges at x=±L/2, y=±W/2
        x_left_hole  = -L/2 + left_pad
        x_right_hole =  L/2 - right_pad
    
        y_center = 0.0
        y_top    =  W/2 - width_pad
        y_bot    = -W/2 + side_pad
    
        hole_pts = [
            (x_left_hole,  y_center),  # single hole near one end, centered in width
            (x_right_hole, y_top),     # two holes near opposite end, symmetric-ish
            (x_right_hole, y_bot),
        ]
    
        part = (
            plate
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints(hole_pts)
            .hole(hole_d)  # through-hole
        )
    
        # --- Translate so bottom face is at Z=0 (move up by H/2) ---
        part = part.translate((0, 0, H/2))
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00996473/gpt_generated.stl')
