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
        top_len = 120.0
        top_wid = 50.0
        top_thk = 4.0
    
        col_len = 20.0
        col_wid = 30.0
        col_h   = 35.0
    
        end_margin = 10.0  # distance from each end of the top to the nearest column face
    
        # Column center positions along X (symmetric)
        x_off = (top_len / 2.0) - end_margin - (col_len / 2.0)
        col_pts = [(-x_off, 0.0), (x_off, 0.0)]
    
        # --- Model ---
        result = (
            cq.Workplane("XY")
            # Top plate
            .rect(top_len, top_wid)
            .extrude(top_thk)
            # Two columns on top face, symmetric at each end
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints(col_pts)
            .rect(col_len, col_wid)
            .extrude(col_h)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00997677/gpt_generated.stl')
