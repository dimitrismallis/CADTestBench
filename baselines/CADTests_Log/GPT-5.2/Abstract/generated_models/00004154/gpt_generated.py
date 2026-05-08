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
        # Parameters (mm)
        length = 60.0
        width = 30.0
        r = 6.0
        height = 12.0
    
        if r <= 0:
            profile = cq.Workplane("XY").rect(length, width)
        else:
            if 2 * r > min(length, width):
                raise ValueError("corner radius too large for given length/width")
    
            hx = length / 2.0
            hy = width / 2.0
    
            # Build rounded rectangle wire (counter-clockwise) using tangent lines + quarter arcs
            profile = (
                cq.Workplane("XY")
                .moveTo(-hx + r, -hy)                 # start on bottom edge, after bottom-left corner
                .lineTo(hx - r, -hy)                  # bottom edge
                .radiusArc((hx, -hy + r), r)          # bottom-right corner
                .lineTo(hx, hy - r)                   # right edge
                .radiusArc((hx - r, hy), r)           # top-right corner
                .lineTo(-hx + r, hy)                  # top edge
                .radiusArc((-hx, hy - r), r)          # top-left corner
                .lineTo(-hx, -hy + r)                 # left edge
                .radiusArc((-hx + r, -hy), r)         # bottom-left corner back to start
                .close()
            )
    
        result = profile.extrude(height)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00004154/gpt_generated.stl')
