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
        # Parameters
        square_side = 40.0
        extrude_h = 15.0
    
        half = square_side / 2.0
        r = square_side / 2.0  # semicircle radius so its diameter matches the square width
    
        # Build a "house" profile: square + semicircle on top
        profile = (
            cq.Workplane("XY")
            .moveTo(-half, -half)          # bottom-left of square
            .lineTo(half, -half)           # bottom edge
            .lineTo(half, half)            # right edge up to top-right
            # semicircle from (half, half) to (-half, half) bulging upward
            .threePointArc((0, half + r), (-half, half))
            .lineTo(-half, -half)          # left edge back down
            .close()
        )
    
        result = profile.extrude(extrude_h)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00984488/gpt_generated.stl')
