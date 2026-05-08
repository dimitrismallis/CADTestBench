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
        plate_h = 60.0                 # height in Y
        plate_w = (2.0 / 3.0) * plate_h  # width in X (about 2/3 of height)
        plate_t = 12.0                 # thickness in Z
    
        slot_w = 8.0                   # slot width in X (narrow)
        slot_h = plate_h               # runs bottom-to-top of the front profile
    
        # --- Base plate ---
        plate = cq.Workplane("XY").rect(plate_w, plate_h).extrude(plate_t)
    
        # --- Slotted groove cut from the front profile (front = -Y face) ---
        result = (
            plate
            .faces("<Y").workplane(centerOption="CenterOfMass")
            .rect(slot_w, slot_h)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00996962/gpt_generated.stl')
