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
        page_w = 210.0      # width (X)
        page_h = 297.0      # height (Y)
        page_t = 2.0        # thickness (Z) - "small amount"
    
        hole_d = 6.0
        hole_margin_x = 12.0   # distance from left edge to hole center
        hole_margin_y = 25.0   # distance from top/bottom edge to hole center
    
        # --- Base page ---
        page = cq.Workplane("XY").rect(page_w, page_h).extrude(page_t)
    
        # --- Two hole-punch holes on the left side (top and bottom) ---
        # Use a construction rectangle to get the two Y positions (top/bottom),
        # and then shift left to the desired X position.
        holes = (
            page.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .center(-page_w / 2 + hole_margin_x, 0)
            .rect(0.001, page_h - 2 * hole_margin_y, forConstruction=True)  # tiny width, just to create 2 vertices
            .vertices()
            .hole(hole_d)
        )
    
        return holes
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00670454/gpt_generated.stl')
