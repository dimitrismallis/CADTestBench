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
        overall_len = 120.0
        width = 30.0                 # diameter of semicircle ends
        thickness = 4.0
    
        hole_d = 6.0
        hole_offset_x = 0.0          # from each end-center along X (0 = at end center)
    
        r = width / 2.0
        straight_len = overall_len - 2.0 * r
        x_end = straight_len / 2.0
    
        # --- Capsule outline as a single closed wire (fluent 2D) ---
        # Start at top-left of the straight section, go to top-right,
        # arc around right end, go to bottom-left, arc around left end, close.
        profile = (
            cq.Workplane("XY")
            .moveTo(-x_end,  r)
            .lineTo( x_end,  r)
            .radiusArc(( x_end, -r), -r)   # right semicircle (clockwise)
            .lineTo(-x_end, -r)
            .radiusArc((-x_end,  r), -r)   # left semicircle (clockwise)
            .close()
        )
    
        plate = profile.extrude(thickness)
    
        # --- Holes near centers of semicircular ends ---
        hole_pts = [
            ( x_end + hole_offset_x, 0.0),
            (-x_end - hole_offset_x, 0.0),
        ]
    
        plate = (
            plate.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .pushPoints(hole_pts)
            .hole(hole_d)
        )
    
        return plate
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00032961/gpt_generated.stl')
