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
        v_height = 80.0          # vertical leg height (dominant)
        v_width  = 18.0          # vertical leg thickness in X
        h_length = 32.0          # horizontal leg length (significantly smaller than v_height)
        h_height = 14.0          # horizontal leg thickness in Y
        curve_out = 6.0          # outward bulge of the vertical leg outer edge
        extrude_thk = 12.0       # extrusion thickness in Z
    
        # Build an L shape as a single closed wire:
        # Coordinate system: X to the right, Y up in sketch plane.
        # L occupies: vertical leg from x=[0..v_width], y=[0..v_height]
        #             horizontal foot from x=[0..h_length], y=[0..h_height]
        #
        # Make the *outer* right edge of the vertical leg slightly curved (bulging outward).
        # We'll define a boundary that goes around the outside of the L, using a spline on the
        # right side of the vertical leg.
    
        # Key points around the perimeter (counter-clockwise)
        p0 = (0.0, 0.0)                 # bottom-left
        p1 = (h_length, 0.0)            # bottom-right of foot
        p2 = (h_length, h_height)       # top-right of foot
        p3 = (v_width, h_height)        # inner corner on right side of vertical leg
        p4 = (v_width, v_height)        # top-right nominal of vertical leg
        p5 = (0.0, v_height)            # top-left
        p6 = (0.0, h_height)            # down left side to inner corner
        p7 = (0.0, h_height)            # same as p6 (explicit for clarity)
        p8 = (0.0, 0.0)                 # close
    
        # Spline control points for the curved outer edge from p3->p4 (right side of vertical leg)
        # Bulge outward in +X direction.
        c1 = (v_width + curve_out, h_height + 0.35 * (v_height - h_height))
        c2 = (v_width + 0.6 * curve_out, h_height + 0.75 * (v_height - h_height))
    
        profile = (
            cq.Workplane("XY")
            .moveTo(*p0)
            .lineTo(*p1)
            .lineTo(*p2)
            .lineTo(*p3)
            .spline([c1, c2, p4])   # curved outer edge up to the top
            .lineTo(*p5)
            .lineTo(*p6)
            .close()
        )
    
        result = profile.extrude(extrude_thk)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00995733/gpt_generated.stl')
