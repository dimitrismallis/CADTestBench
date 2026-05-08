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
        bulb_d = 0.358436
        bulb_r = bulb_d / 2.0
    
        rect_len_x = 0.192347          # rectangle length (X)
        rect_w = 0.592709              # rectangle width reference
        rect_h_y = 7.0 * rect_w        # height approx 7x its width (Y)
    
        overlap = 0.02193
    
        hole_d = 0.052367
        hole_offset_from_top = 0.048552  # distance from top edge of rectangle
    
        extrude_depth = 0.029536
    
        # --- Layout ---
        # Bulb circle centered at origin.
        # Stem rectangle centered in X, extends in +Y, with bottom overlapping into circle by `overlap`.
        circle_top_y = bulb_r
        rect_bottom_y = circle_top_y - overlap
        rect_center_y = rect_bottom_y + rect_h_y / 2.0
    
        # Hole near top edge of rectangle, offset downward by hole_offset_from_top
        hole_center = (0.0, (rect_bottom_y + rect_h_y) - hole_offset_from_top)
    
        # --- Build 2D face using Sketch, then extrude ---
        sk = (
            cq.Sketch()
            .circle(bulb_r)                          # additive bulb
            .rect(rect_len_x, rect_h_y).moved(0, rect_center_y)  # additive stem
            .circle(hole_d / 2.0, mode="s").moved(*hole_center)  # subtract hole
        )
    
        result = cq.Workplane("XY").placeSketch(sk).extrude(extrude_depth)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00998074/gpt_generated.stl')
