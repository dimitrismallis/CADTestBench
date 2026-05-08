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
        top_length = 120.0
        top_width  = 80.0
        top_thk    = 8.0
    
        leg_size   = 10.0   # square leg cross-section
        leg_height = 70.0   # how far legs extend downward from underside of top
    
        # Corner locations for legs (center points of leg squares)
        x = top_length / 2 - leg_size / 2
        y = top_width  / 2 - leg_size / 2
        leg_pts = [( x,  y), ( x, -y), (-x,  y), (-x, -y)]
    
        # --- Model ---
        top = cq.Workplane("XY").box(top_length, top_width, top_thk, centered=True)
    
        table = (
            top
            .faces("<Z").workplane(centerOption="CenterOfMass")
            .pushPoints(leg_pts)
            .rect(leg_size, leg_size)
            .extrude(-leg_height, combine=True)  # extrude downward from underside
        )
    
        return table
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00001817/gpt_generated.stl')
