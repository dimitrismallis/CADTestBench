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
        # --- Parameters (units as given in prompt) ---
        horiz_len = 0.024896
        curve_rise = 0.752339
        straight_rise = 0.12
        extrude_depth = 0.018672
    
        # Use a sweep of a thin rectangle to form the L "stroke"
        stroke_w = 0.06  # width of the L stroke in XY
        stroke_h = extrude_depth  # extrude depth in Z
    
        x = horiz_len
        y_curve_end = curve_rise
        y_top = curve_rise + straight_rise
    
        # Path: short horizontal, then a gentle arc up, then straight up.
        # Arc defined by end point and a mid point to create curvature.
        p0 = (0.0, 0.0)
        p1 = (x, 0.0)
    
        # Arc end at (x, y_curve_end). Midpoint slightly to +X to create curvature.
        mid = (x + 0.012, y_curve_end * 0.45)
        p2 = (x, y_curve_end)
        p3 = (x, y_top)
    
        path = (
            cq.Workplane("XY")
            .moveTo(*p0)
            .lineTo(*p1)
            .threePointArc(mid, p2)
            .lineTo(*p3)
            .wire()
        )
    
        # Profile rectangle (in a plane normal to path start; easiest: YZ plane at origin)
        # We'll sweep along the path; keep it centered on the path.
        profile = cq.Workplane("YZ").rect(stroke_w, stroke_h, centered=True)
    
        result = profile.sweep(path, isFrenet=True)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00995733/gpt_generated.stl')
