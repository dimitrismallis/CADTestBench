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
        R_big = 25.0
        R_small = 12.0
        center_dist = 2.0 * R_big          # approx equal to diameter of larger circle
        thickness = 8.0                    # extrusion height
    
        # Centers on XY plane
        c1 = (0.0, 0.0)                    # big circle center
        c2 = (center_dist, 0.0)            # small circle center
    
        # --- Compute external tangency points for the two common external tangents ---
        # For circles with centers separated along +X:
        # Let alpha = acos((R1 - R2)/d). Tangent points are:
        # P1 = C1 + R1*(cos(alpha),  sin(alpha)) and C1 + R1*(cos(alpha), -sin(alpha))
        # P2 = C2 + R2*(cos(alpha),  sin(alpha)) and C2 + R2*(cos(alpha), -sin(alpha))
        d = center_dist
        if d <= abs(R_big - R_small):
            raise ValueError("Circle centers too close for external tangents with given radii.")
    
        alpha = math.acos((R_big - R_small) / d)
        ca, sa = math.cos(alpha), math.sin(alpha)
    
        p1_top = (c1[0] + R_big * ca,   c1[1] + R_big * sa)
        p1_bot = (c1[0] + R_big * ca,   c1[1] - R_big * sa)
        p2_top = (c2[0] + R_small * ca, c2[1] + R_small * sa)
        p2_bot = (c2[0] + R_small * ca, c2[1] - R_small * sa)
    
        # --- Build a single closed wire: top tangent -> small arc -> bottom tangent -> big arc ---
        wp = cq.Workplane("XY")
    
        # Start at top tangency on big circle, go to top tangency on small circle (straight)
        profile = (
            wp
            .moveTo(p1_top[0], p1_top[1])
            .lineTo(p2_top[0], p2_top[1])
            # Arc around small circle from top tangency to bottom tangency (right side)
            .radiusArc(p2_bot, -R_small)   # negative radius chooses the "other" arc (the longer/right-side arc)
            # Bottom tangent back to big circle
            .lineTo(p1_bot[0], p1_bot[1])
            # Arc around big circle from bottom tangency back to top tangency (left side)
            .radiusArc(p1_top, -R_big)
            .close()
        )
    
        # Extrude to create the 3D object
        result = profile.extrude(thickness)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00037276/gpt_generated.stl')
