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
        square_size = 40.0          # side length of the main square
        tab_width = 6.0             # tab width (in X direction)
        tab_height = 2.0 * tab_width  # tab height (in Y direction), per request
        depth = 4.0                 # small extrusion depth
    
        half = square_size / 2.0
    
        # Build a closed profile: square with left/right rectangular tabs
        profile = (
            cq.Workplane("XY")
            # main square
            .rect(square_size, square_size)
            # left tab (centered on y=0, attached to left edge at x=-half)
            .center(-half - tab_width / 2.0, 0)
            .rect(tab_width, tab_height)
            .center(half + tab_width / 2.0 + half + tab_width / 2.0, 0)  # move from left-tab center to right-tab center
            # right tab (centered on y=0, attached to right edge at x=+half)
            .rect(tab_width, tab_height)
            # make a single face from the union of the overlapping rectangles
            .combine()
        )
    
        result = profile.extrude(depth)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00997065/gpt_generated.stl')
