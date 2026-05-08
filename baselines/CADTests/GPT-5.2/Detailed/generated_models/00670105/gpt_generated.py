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
        # --- Parameters (units as given) ---
        rect_h = 0.2727275
        rect_len = 0.477273
        tri_base = 0.204545
        prism_width = 0.75  # extrusion distance in +Z
    
        # Derived: triangle height so that its base endpoints meet the rectangle's top corners
        # Rectangle top corners are at x = ±rect_len/2, y = rect_h
        # Triangle base endpoints are at x = ±tri_base/2, y = rect_h
        # Triangle sides connect from rectangle top corners to apex at x=0, y=rect_h + tri_h
        tri_h = math.sqrt(max((rect_len - tri_base) * (rect_len + tri_base), 0.0)) / 2.0
    
        # Key points (centered about X=0, bottom at Y=0)
        xL, xR = -rect_len / 2.0, rect_len / 2.0
        xbL, xbR = -tri_base / 2.0, tri_base / 2.0
        y0, y1 = 0.0, rect_h
        apex = (0.0, rect_h + tri_h)
    
        # Pentagon vertices in order (counter-clockwise)
        pts = [
            (xL, y0),      # bottom-left
            (xR, y0),      # bottom-right
            (xR, y1),      # top-right of rectangle
            apex,          # apex
            (xL, y1),      # top-left of rectangle
        ]
    
        result = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(prism_width)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00670105/gpt_generated.stl')
