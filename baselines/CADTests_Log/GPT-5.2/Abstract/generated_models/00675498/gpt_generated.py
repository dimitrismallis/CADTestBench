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
        rect_len = 80.0          # larger side
        rect_wid = 40.0          # smaller side ~ half of larger
        trap_len = 40.0          # extension length of trapezoid
        trap_h_long = rect_wid   # longer base matches rectangle end
        trap_h_short = 20.0      # shorter base (creates the "tier" step)
        height = 20.0            # extrusion height
    
        # Rectangle centered at origin, spanning x in [-rect_len/2, +rect_len/2]
        xR = rect_len / 2.0
        yH = rect_wid / 2.0
    
        # Trapezoid attached to rectangle's +X end (at x = xR)
        # Right trapezoid: left side vertical, right side slanted
        xT = xR + trap_len
        yT_short = trap_h_short / 2.0
    
        # Build a single closed outline (counter-clockwise)
        pts = [
            (-xR, -yH),          # rectangle bottom-left
            ( xR, -yH),          # rectangle bottom-right (attachment start)
            ( xT, -yT_short),    # trapezoid bottom-right
            ( xT,  yT_short),    # trapezoid top-right
            ( xR,  yH),          # trapezoid top-left (attachment end)
            (-xR,  yH),          # rectangle top-left
        ]
    
        result = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(height)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00675498/gpt_generated.stl')
