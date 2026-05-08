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
        long_leg_len = 120.0      # overall length in X
        short_leg_len = 60.0      # overall length in Y
        leg_width = 20.0          # width of each leg
        bracket_thickness = 6.0   # extrusion thickness in Z
    
        L = long_leg_len
        S = short_leg_len
        w = leg_width
    
        # Define an L-shaped polygon (counter-clockwise), centered about origin.
        # Outer extents: X in [-L/2, L/2], Y in [-S/2, S/2]
        # Cutout (missing quadrant) is top-right: X in [L/2-w, L/2], Y in [S/2-w, S/2]
        pts = [
            (-L/2, -S/2),
            ( L/2, -S/2),
            ( L/2,  S/2 - w),
            (-L/2 + w,  S/2 - w),
            (-L/2 + w,  S/2),
            (-L/2,  S/2),
        ]
    
        result = (
            cq.Workplane("XY")
            .moveTo(*pts[0])
            .lineTo(*pts[1])
            .lineTo(*pts[2])
            .lineTo(*pts[3])
            .lineTo(*pts[4])
            .lineTo(*pts[5])
            .close()
            .extrude(bracket_thickness)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00672291/gpt_generated.stl')
