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
        # Parameters (mm)
        base_len = 60.0
        base_wid = 40.0
        base_thk = 10.0
    
        slot_len = base_len * 0.5
        slot_wid = base_wid * 0.5
        slot_depth = 4.0  # smaller than base_thk to create a pocket/slot
    
        # Base solid
        result = (
            cq.Workplane("XY")
            .rect(base_len, base_wid)
            .extrude(base_thk)
        )
    
        # Slot cut (recess) from the top face, centered
        result = (
            result
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .rect(slot_len, slot_wid)
            .cutBlind(-slot_depth)  # negative distance cuts downward into the solid
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00997580/gpt_generated.stl')
