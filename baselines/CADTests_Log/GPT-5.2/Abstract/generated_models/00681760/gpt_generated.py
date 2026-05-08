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
        rect_len = 80.0   # larger side of rectangle (X direction)
        rect_wid = 40.0   # smaller side of rectangle (Y direction)
    
        trap_height = 25.0          # distance from shared edge to longer base (in +Y)
        trap_long_base = rect_len   # longer base equals rectangle's larger side
        trap_short_base = 50.0      # smaller base (this will attach to rectangle)
    
        extrude_h = 120.0           # "large amount"
    
        # --- Derived geometry ---
        # Place rectangle centered at origin, spanning y in [-rect_wid/2, +rect_wid/2]
        y_top = rect_wid / 2.0
    
        # Trapezoid attaches via its shorter base to the rectangle's top long edge (y = y_top)
        # Isosceles trapezoid: longer base centered on same x=0 centerline
        x_short_left = -trap_short_base / 2.0
        x_short_right = trap_short_base / 2.0
        x_long_left = -trap_long_base / 2.0
        x_long_right = trap_long_base / 2.0
    
        y_short = y_top
        y_long = y_top + trap_height
    
        # --- Build 2D profile as a single closed wire ---
        # Outline goes around the union of rectangle + trapezoid without internal edges.
        pts = [
            (-rect_len/2.0, -rect_wid/2.0),   # rectangle bottom-left
            ( rect_len/2.0, -rect_wid/2.0),   # bottom-right
            ( rect_len/2.0,  y_top),          # top-right of rectangle
            ( x_short_right, y_short),        # along top edge to trapezoid short base right
            ( x_long_right,  y_long),         # up/right to trapezoid long base right
            ( x_long_left,   y_long),         # across long base
            ( x_short_left,  y_short),        # down/left to short base left
            (-rect_len/2.0,  y_top),          # back to rectangle top-left
        ]
    
        profile = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
        )
    
        # --- Extrude to 3D ---
        result = profile.extrude(extrude_h)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00681760/gpt_generated.stl')
