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
        # Parameters (units as given in prompt)
        L = 0.875
        W = 0.15
        H = 1.5
    
        fillet_r_req = 0.25
    
        hole_d = 0.3
        pad = -0.639071  # used to adjust point-placement rectangle
    
        # Fillet radius must be <= min(L/2, W/2) for a rectangle corner
        fillet_r_max = min(L, W) / 2.0
        fillet_r = min(fillet_r_req, fillet_r_max * 0.999)  # tiny margin for robustness
    
        # --- Base solid: rectangle with two corners on the same long edge filleted ---
        prof = (
            cq.Sketch()
            .rect(L, W)
            # Fillet the two vertices on the +Y side (one long edge)
            .vertices(">Y").fillet(fillet_r)
        )
    
        part = cq.Workplane("XY").placeSketch(prof).extrude(H)
    
        # --- Holes on the same side as the rounded corners ---
        # Use a construction rectangle to generate two points near the +Y corners.
        hole_pts_rect_x = L + pad
        hole_pts_rect_y = W + pad
    
        # Ensure positive sizes for the construction rectangle
        hole_pts_rect_x = max(1e-3, hole_pts_rect_x)
        hole_pts_rect_y = max(1e-3, hole_pts_rect_y)
    
        part = (
            part
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(hole_pts_rect_x, hole_pts_rect_y, forConstruction=True)
            .vertices(">Y")  # the two points on the +Y side (same side as fillets)
            .hole(hole_d)
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00986712/gpt_generated.stl')
