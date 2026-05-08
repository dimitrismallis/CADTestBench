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
        cyl_d = 80.0          # main cylinder diameter
        cyl_h = 15.0          # main cylinder height (short)
    
        center_hole_d = cyl_d / 8.0  # per request: 1/8th diameter of cylinder
    
        # Three smaller holes
        small_hole_d = center_hole_d * 0.5   # "even smaller" than the center hole
        bolt_circle_r = center_hole_d * 1.2  # radius from center for triangular pattern
    
        # --- Model ---
        result = (
            cq.Workplane("XY")
            .circle(cyl_d / 2.0)
            .extrude(cyl_h)
            # Center through-hole
            .faces(">Z").workplane()
            .hole(center_hole_d)
            # Three small holes in triangular formation (120° apart)
            .faces(">Z").workplane()
            .polarArray(bolt_circle_r, 0, 360, 3)
            .hole(small_hole_d)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00997300/gpt_generated.stl')
