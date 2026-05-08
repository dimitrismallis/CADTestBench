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
        side = 40.0
        corner_r = 6.0
        height = 12.0
    
        # 2D rounded square via Sketch (2D fillet), then extrude
        rounded_square = (
            cq.Sketch()
            .rect(side, side)
            .vertices()
            .fillet(corner_r)
        )
    
        result = cq.Workplane("XY").placeSketch(rounded_square).extrude(height)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00521969/gpt_generated.stl')
