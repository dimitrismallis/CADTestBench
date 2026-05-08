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
        # --- Parameters ---
        width = 60.0          # overall width of the pentagon
        rect_h = 35.0         # height of the rectangular lower part
        roof_h = 25.0         # height of the triangular upper part
        prism_h = 40.0        # extrusion height
    
        # 5 vertices: bottom-left, bottom-right, top-right of rectangle,
        # roof peak, top-left of rectangle (then close back to start)
        pts = [
            (-width/2, 0.0),
            ( width/2, 0.0),
            ( width/2, rect_h),
            ( 0.0,     rect_h + roof_h),
            (-width/2, rect_h),
        ]
    
        result = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(prism_h)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00670105/gpt_generated.stl')
