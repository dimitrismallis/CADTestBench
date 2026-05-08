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
        bottom_width = 60.0   # wider base
        top_width = 30.0      # narrower top
        height_2d = 25.0      # trapezoid height in the sketch (Y direction)
        prism_length = 40.0   # extrusion distance (+Z)
    
        # Trapezoid vertices (centered about X=0, with bottom at y=0)
        x1 = -bottom_width / 2
        x2 =  bottom_width / 2
        x3 =  top_width / 2
        x4 = -top_width / 2
        y0 = 0.0
        y1 = height_2d
    
        trapezoid = (
            cq.Workplane("XY")
            .moveTo(x1, y0)
            .lineTo(x2, y0)
            .lineTo(x3, y1)
            .lineTo(x4, y1)
            .close()
            .extrude(prism_length)
        )
    
        return trapezoid
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00675952/gpt_generated.stl')
