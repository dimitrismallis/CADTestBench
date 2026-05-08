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
        rect_w = 0.399631   # along X
        rect_h = 0.091591   # along Y
        extrude_h = 0.133054
    
        # Semi-hex section constraints
        span = (2.0 / 3.0) * rect_w          # along X, starting at left end
        max_width = 0.188808                 # maximum overall width of semi-hex (in Y)
        add_height = max_width - rect_h      # extension beyond rectangle height
        add_height = max(add_height, 0.0)
    
        # Rectangle placed with lower-left at origin (0,0)
        # Semi-hex attaches to the long top edge y=rect_h, starting at x=0 and ending at x=span
        x0 = 0.0
        x1 = span
        y0 = rect_h
        y_mid = rect_h + 0.5 * add_height
        y_top = rect_h + add_height
    
        semi_hex_pts = [
            (x0, y0),
            (x1, y0),
            (x1, y_mid),
            (0.75 * span, y_top),
            (0.25 * span, y_top),
            (x0, y_mid),
        ]
    
        sk = (
            cq.Sketch()
            # base rectangle: lower-left at (0,0)
            .push([(rect_w / 2.0, rect_h / 2.0)])
            .rect(rect_w, rect_h)
            .reset()
            # semi-hex polygon: defined in absolute coordinates, then assembled as a face and unioned
            .polygon(semi_hex_pts, mode="a")
        )
    
        result = cq.Workplane("XY").placeSketch(sk).extrude(extrude_h)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00996368/gpt_generated.stl')
