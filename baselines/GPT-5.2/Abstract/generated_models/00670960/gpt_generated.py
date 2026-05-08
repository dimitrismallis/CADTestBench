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
        rect_len = 60.0   # X direction (slightly longer)
        rect_wid = 54.0   # Y direction (shorter edge length)
    
        base = (2.0 / 3.0) * rect_wid          # trapezium base attached to rectangle short edge
        leg = 0.10 * base                      # angular side length
        base_angle_deg = 45.0
    
        base_angle = math.radians(base_angle_deg)
        height = leg * math.sin(base_angle)
        inset_each_side = leg * math.cos(base_angle)
        top = max(0.5, base - 2.0 * inset_each_side)
    
        # Attach trapezium base to rectangle's shorter edge (top edge y=+rect_wid/2)
        y_base = rect_wid / 2.0
        x_offset = 2.0  # slightly right of center
    
        p1 = (x_offset - base / 2.0, y_base)
        p2 = (x_offset + base / 2.0, y_base)
        p3 = (x_offset + top / 2.0,  y_base + height)
        p4 = (x_offset - top / 2.0,  y_base + height)
    
        thickness = 2.0
    
        # Build both closed wires in one workplane, combine into a single face, then extrude
        profile = (
            cq.Workplane("XY")
            .rect(rect_len, rect_wid)          # closed wire 1 (pending)
            .moveTo(*p1).lineTo(*p2).lineTo(*p3).lineTo(*p4).close()  # closed wire 2 (pending)
            .combine()                         # make a single face from all pending wires
        )
    
        result = profile.extrude(thickness)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00670960/gpt_generated.stl')
