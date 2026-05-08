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
        w = 20.0                 # base rectangle width
        h = w / 20.0             # thin base rectangle height
        s1 = w / 2.0             # first square side ~ half the base width
        s2 = s1 * 0.85           # second square slightly smaller
        depth = 20.0 * w         # extrusion depth ~ 20x base width
    
        # Key x/y coordinates
        xL = -w / 2.0
        xR =  w / 2.0
    
        # First square is right-aligned to xR, sits on top of base
        x1L = xR - s1
        y0 = 0.0
        y1 = h
        y2 = h + s1
    
        # Second square is right-aligned to xR, sits on top of first square
        x2L = xR - s2
        y3 = y2 + s2
    
        # Build a single closed outline (counter-clockwise) that matches the union shape
        pts = [
            (xL, y0),   # bottom-left of base
            (xR, y0),   # bottom-right of base
            (xR, y3),   # up right side to top of 2nd square
            (x2L, y3),  # left along top of 2nd square
            (x2L, y2),  # down to top of 1st square
            (x1L, y2),  # left along top of 1st square
            (x1L, y1),  # down to top of base
            (xL, y1),   # left along top of base
        ]
    
        profile = (
            cq.Workplane("XY")
            .moveTo(*pts[0])
            .lineTo(*pts[1])
            .lineTo(*pts[2])
            .lineTo(*pts[3])
            .lineTo(*pts[4])
            .lineTo(*pts[5])
            .lineTo(*pts[6])
            .lineTo(*pts[7])
            .close()
        )
    
        result = profile.extrude(depth)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00997040/gpt_generated.stl')
