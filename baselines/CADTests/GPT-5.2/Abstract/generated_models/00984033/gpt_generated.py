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
        plate_len = 120.0   # X
        plate_wid = 60.0    # Y
        plate_thk = 6.0     # Z
    
        hole_d = 8.0
        edge_margin_x = 15.0   # distance from left edge to first hole center
        edge_margin_y = 12.0   # distance from top edge to hole centers
        hole_pitch = 18.0      # spacing along length (X)
    
        # Hole centers near top-left corner, running along length (+X)
        x0 = -plate_len / 2 + edge_margin_x
        y0 =  plate_wid / 2 - edge_margin_y
        pts = [(x0 + i * hole_pitch, y0) for i in range(3)]
    
        # --- Model ---
        plate = cq.Workplane("XY").rect(plate_len, plate_wid).extrude(plate_thk)
    
        result = (
            plate
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints(pts)
            .circle(hole_d / 2)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00984033/gpt_generated.stl')
