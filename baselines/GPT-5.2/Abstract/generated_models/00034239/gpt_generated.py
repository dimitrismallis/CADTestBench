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
        plate_w = 60.0
        plate_h = 60.0
        plate_t = 6.0
    
        big_hole_d = 30.0
        small_hole_d = 8.0
        small_hole_offset_x = 22.0  # center-to-center from the big hole along X
    
        # --- Model ---
        result = (
            cq.Workplane("XY")
            .rect(plate_w, plate_h)
            .extrude(plate_t)
            # Large center hole
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .hole(big_hole_d)
            # Two small holes left/right of center
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints([(-small_hole_offset_x, 0), (small_hole_offset_x, 0)])
            .hole(small_hole_d)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00034239/gpt_generated.stl')
