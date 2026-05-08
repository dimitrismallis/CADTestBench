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
        side = 0.86802
        r = side / 2.0
        h = 0.152284
    
        # Build a single closed 2D profile:
        # Start at bottom-left of square, go around square to top-left,
        # then draw a semicircle (top half) from top-left to top-right with center at (0, side/2),
        # then close back to start.
        xL, xR = -side / 2.0, side / 2.0
        yB, yT = -side / 2.0, side / 2.0
    
        profile = (
            cq.Workplane("XY")
            .moveTo(xL, yB)          # bottom-left
            .lineTo(xR, yB)          # bottom-right
            .lineTo(xR, yT)          # top-right (end of square)
            # semicircle: from top-right to top-left, bulging upward
            .threePointArc((0.0, yT + r), (xL, yT))
            .close()
        )
    
        result = profile.extrude(h)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00984488/gpt_generated.stl')
