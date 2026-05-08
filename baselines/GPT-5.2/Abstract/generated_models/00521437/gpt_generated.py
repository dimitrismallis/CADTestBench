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
        base_len = 120.0          # long dimension
        base_wid = 10.0           # thin dimension (len is 12x width)
        base_thk = 4.0            # slight extrusion
    
        # Holes: slightly less than half the base size, with clear margins
        hole_len = 48.0           # < base_len/2 = 60
        hole_wid = 4.0            # < base_wid/2 = 5
        edge_margin_x = 8.0       # keep away from left/right edges
        edge_margin_y = 2.0       # keep away from front/back edges
        gap_between_holes = 8.0   # ensure holes don't touch each other
    
        # Compute symmetric hole center positions along X
        # Ensure: 2*(hole_len/2 + edge_margin_x) + gap <= base_len
        needed = 2 * (hole_len / 2 + edge_margin_x) + gap_between_holes
        if needed > base_len:
            # fallback: reduce hole length to fit constraints
            hole_len = max(1.0, base_len - (2 * edge_margin_x + gap_between_holes))
    
        x_center = (gap_between_holes / 2.0) + (hole_len / 2.0)
        hole_centers = [(-x_center, 0.0), (x_center, 0.0)]
    
        # --- Model ---
        base = cq.Workplane("XY").rect(base_len, base_wid).extrude(base_thk)
    
        result = (
            base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints(hole_centers)
            .rect(hole_len, hole_wid)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00521437/gpt_generated.stl')
