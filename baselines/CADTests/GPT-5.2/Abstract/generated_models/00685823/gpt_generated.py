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
        side = 40.0          # square side length
        cut_radius = 12.0    # radius of the circular corner cutout
        height = 15.0        # extrusion height
    
        # Square centered at origin => top-right corner at (side/2, side/2)
        cx = side / 2.0
        cy = side / 2.0
    
        # 2D sketch: square with a quarter-circle removed from the top-right corner
        sk = (
            cq.Sketch()
            .rect(side, side)                 # base square (add)
            .push([(cx, cy)])                 # move to top-right corner
            .circle(cut_radius, mode="s")     # subtract circle; only overlapping quadrant is removed
        )
    
        # Extrude the resulting face
        result = cq.Workplane("XY").placeSketch(sk).extrude(height)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00685823/gpt_generated.stl')
