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
        rect_len = 90.0   # rectangle length along X (longer edge)
        rect_w   = 40.0   # rectangle width along Y
        t        = 12.0   # extrusion thickness along Z
    
        # Semi-hexagon parameters
        semi_len = (2.0 / 3.0) * rect_len   # along X, starts at left end
        cap_h    = 18.0                    # how far it extends beyond the rectangle in +Y
        top_frac = 0.55                    # top edge length as fraction of base (smaller edge)
    
        # Derived
        x0 = -rect_len / 2.0
        x1 = x0 + semi_len
        y_top_rect = rect_w / 2.0
    
        base_len = semi_len
        top_len = base_len * top_frac
        x_mid = (x0 + x1) / 2.0
        xt0 = x_mid - top_len / 2.0
        xt1 = x_mid + top_len / 2.0
    
        # Build a single outline:
        # Start at bottom-left of rectangle, go around rectangle,
        # but replace the top edge segment from x0..x1 with the semi-hex cap.
        pts = [
            (x0, -rect_w/2.0),          # bottom-left
            ( rect_len/2.0, -rect_w/2.0),# bottom-right
            ( rect_len/2.0,  y_top_rect),# top-right
            (x1,  y_top_rect),          # move left along top edge to end of cap region
            (xt1, y_top_rect + cap_h),  # up-right slant to top edge of cap
            (xt0, y_top_rect + cap_h),  # across top edge of cap (smaller edge)
            (x0,  y_top_rect),          # down-left slant back to rectangle top at left end
            (x0, -rect_w/2.0)           # close
        ]
    
        result = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(t)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00996368/gpt_generated.stl')
