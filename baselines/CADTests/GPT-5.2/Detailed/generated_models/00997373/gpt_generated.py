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
        W = 0.016304
        H = 1.22283
    
        hole_d = 0.130435
        hole_r = hole_d / 2.0
    
        first_from_left = 0.433378
        spacing = 0.195652
        n_holes = 3
    
        # Place holes "towards one side" in Y.
        # Keep them within the part: choose a small margin from the +Y edge.
        y_margin = 0.001  # small offset from the side
        y_pos = (W / 2.0) - y_margin
    
        # X positions measured from left edge of the rectangle
        x0 = -L / 2.0 + first_from_left
        x_positions = [x0 + i * spacing for i in range(n_holes)]
        hole_pts = [(x, y_pos) for x in x_positions]
    
        # --- Model ---
        part = cq.Workplane("XY").box(L, W, H, centered=True)
    
        # Cut holes through entire height (along Z), centered through width (Y is fixed, axis is Z)
        part = (
            part.faces(">Z")
                .workplane(centerOption="CenterOfMass")
                .pushPoints(hole_pts)
                .hole(hole_d)
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00997373/gpt_generated.stl')
