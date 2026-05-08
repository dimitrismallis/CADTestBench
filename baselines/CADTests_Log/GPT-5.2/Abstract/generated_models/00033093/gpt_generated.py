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
        plate_len = 80.0
        plate_wid = 40.0
        plate_thk = 6.0
    
        hole_d = 4.0
        hole_y_offset = 10.0  # symmetric about centerline (Y=0)
        hole_x_offset = 0.0   # keep on center in X; only offset from centerline in Y
    
        # --- Base plate: sketch rectangle then extrude ---
        plate = (
            cq.Workplane("XY")
            .rect(plate_len, plate_wid)
            .extrude(plate_thk)
        )
    
        # --- Cut two symmetric holes from the top face ---
        result = (
            plate
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints([(hole_x_offset, hole_y_offset), (hole_x_offset, -hole_y_offset)])
            .circle(hole_d / 2.0)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00033093/gpt_generated.stl')
