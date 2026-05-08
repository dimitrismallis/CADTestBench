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
        # --- Parameters (units as given) ---
        L = 1.5
        W = 1.37143
        H = 0.078171
    
        slot_len_x = 0.085714          # slot length along X
        slot_height_z = H              # spans full plate height
        slot_start_from_left = 0.685714  # from left edge of plate to slot start (in X)
    
        # Derived: slot center X position in global coordinates (plate centered at X=0)
        # Left edge is at x = -L/2. Slot start is at x = -L/2 + slot_start_from_left.
        # Slot center is start + slot_len_x/2.
        slot_center_x = (-L / 2.0) + slot_start_from_left + (slot_len_x / 2.0)
    
        # --- Base plate ---
        plate = cq.Workplane("XY").rect(L, W).extrude(H)
    
        # --- Slot cut from the front profile (front = -Y face) ---
        # Cut through the plate in Y direction (through all).
        result = (
            plate
            .faces("<Y").workplane(centerOption="CenterOfMass")
            .center(slot_center_x, 0)          # X offset; Z is handled by centering the rectangle
            .rect(slot_len_x, slot_height_z)   # rectangle in X-Z plane on the front face
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00996962/gpt_generated.stl')
