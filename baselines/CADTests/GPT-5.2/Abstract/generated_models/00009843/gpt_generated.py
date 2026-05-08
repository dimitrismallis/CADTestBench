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
        base_wx = 60.0   # X width (left-right)
        base_wy = 30.0   # Y width (front-back)
        base_h  = 4.0
    
        step_side_shrink = 6.0  # total shrink in X (left+right), Y unchanged
        step_h = 3.0
    
        trap_h = 6.0
        trap_bottom_wx = base_wx - step_side_shrink  # matches 2nd rectangle width
        trap_top_wx = trap_bottom_wx + 8.0           # slightly longer than 2nd rectangle
        trap_wy = base_wy                             # keep same depth
        trap_taper_deg = math.degrees(math.atan((trap_top_wx - trap_bottom_wx) / 2.0 / trap_h))
    
        # --- Model ---
        result = (
            cq.Workplane("XY")
            # 1) Base rectangle, slight extrude
            .rect(base_wx, base_wy)
            .extrude(base_h)
    
            # 2) Second rectangle on top, smaller only on left/right (X)
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(base_wx - step_side_shrink, base_wy)
            .extrude(step_h)
    
            # 3) Vertically opposite isosceles trapezoid on top (wider at top than at base)
            #    Achieved via tapered extrude: positive taper makes the top larger.
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(trap_bottom_wx, trap_wy)
            .extrude(trap_h, taper=trap_taper_deg)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00009843/gpt_generated.stl')
