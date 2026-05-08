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
        side = 60.0
        cut_d = (2.0 / 3.0) * side
        cut_r = cut_d / 2.0
        thickness = 10.0
    
        # Equilateral triangle (pointing down)
        h = (math.sqrt(3) / 2.0) * side
    
        v_bottom = (0.0, -2.0 * h / 3.0)
        v_left   = (-side / 2.0,  h / 3.0)
        v_right  = ( side / 2.0,  h / 3.0)
    
        # Semicircle endpoints on the bottom "corner" (diameter horizontal)
        p_left  = (v_bottom[0] - cut_r, v_bottom[1])
        p_right = (v_bottom[0] + cut_r, v_bottom[1])
    
        # Build a single closed profile:
        # left vertex -> right vertex -> to right semicircle endpoint -> semicircle arc to left endpoint (bulging upward)
        # -> back to left vertex -> close
        profile = (
            cq.Workplane("XY")
            .moveTo(*v_left)
            .lineTo(*v_right)
            .lineTo(*p_right)
            # Arc from p_right to p_left with radius=cut_r; choose negative radius to bulge upward
            .radiusArc(p_left, -cut_r)
            .lineTo(*v_left)
            .close()
        )
    
        result = profile.extrude(thickness)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00998714/gpt_generated.stl')
