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
        rect_len = 0.75
        rect_wid = 0.664347
    
        trap_h = 0.374227
        trap_base_short = 0.280836
        trap_base_long  = 0.562673
    
        extrude_depth = 0.664347
    
        # Coordinate helpers
        xL = -rect_len / 2.0
        xR =  rect_len / 2.0
        yRectB = -rect_wid / 2.0
        yRectT =  rect_wid / 2.0
    
        # Trapezoid is attached to rectangle's +X end (xR).
        # Longer base is vertical segment on x=xR, centered on Y.
        yLongB = -trap_base_long / 2.0
        yLongT =  trap_base_long / 2.0
        yShortB = -trap_base_short / 2.0
        yShortT =  trap_base_short / 2.0
    
        xFar = xR + trap_h
    
        # Build a single outer perimeter (counter-clockwise)
        # Start at rectangle bottom-left, go around, detouring around trapezoid on the right.
        pts = [
            (xL, yRectB),     # rect bottom-left
            (xR, yRectB),     # rect bottom-right
            (xR, yLongB),     # up to start of trapezoid long base (bottom)
            (xFar, yShortB),  # to trapezoid short base bottom
            (xFar, yShortT),  # up short base
            (xR, yLongT),     # back to top of long base
            (xR, yRectT),     # up to rect top-right
            (xL, yRectT),     # rect top-left
        ]
    
        profile = (
            cq.Workplane("XY")
            .moveTo(*pts[0])
            .polyline(pts[1:])
            .close()
        )
    
        result = profile.extrude(extrude_depth)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00675498/gpt_generated.stl')
