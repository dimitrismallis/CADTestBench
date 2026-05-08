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
        rect_w = 80.0      # longer edge (X direction)
        rect_h = 40.0      # rectangle height (Y direction)
        tri_h  = 25.0      # height of the isosceles triangle on top
        notch  = 10.0      # size of corner cutouts (legs of right triangles)
        thick  = 3.0       # extrusion thickness
    
        # --- Base pentagon outline: rectangle + isosceles triangle on top ---
        # Rectangle corners (centered about origin)
        x0, x1 = -rect_w/2, rect_w/2
        y0, y1 = -rect_h/2, rect_h/2
        apex = (0.0, y1 + tri_h)
    
        # Outer boundary points (counter-clockwise)
        outer_pts = [
            (x0, y0),      # bottom-left
            (x1, y0),      # bottom-right
            (x1, y1),      # top-right of rectangle
            apex,          # triangle apex
            (x0, y1),      # top-left of rectangle
        ]
    
        # --- Notch triangles at bottom corners (to subtract) ---
        # Left notch: right triangle at bottom-left corner
        left_notch = [
            (x0, y0),
            (x0 + notch, y0),
            (x0, y0 + notch),
        ]
        # Right notch: right triangle at bottom-right corner
        right_notch = [
            (x1, y0),
            (x1 - notch, y0),
            (x1, y0 + notch),
        ]
    
        # Build sketch: add outer face, subtract notches, then extrude
        s = (
            cq.Sketch()
            .polygon(outer_pts)                 # outer boundary
            .polygon(left_notch, mode="s")      # subtract left corner
            .polygon(right_notch, mode="s")     # subtract right corner
        )
    
        result = cq.Workplane("XY").placeSketch(s).extrude(thick)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00997616/gpt_generated.stl')
