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
        # Dimensions (as given; CadQuery units are arbitrary, typically mm)
        base_len = 1.125
        base_wid = 1.5
        base_h   = 0.06
    
        slot_len = 0.3825
        slot_wid = 0.7575
        slot_dep = 0.03  # must be < base_h
    
        # Base solid from sketch + extrude
        base = (
            cq.Workplane("XY")
            .rect(base_len, base_wid)
            .extrude(base_h)
        )
    
        # Slot cut: sketch on top face and negatively extrude (cut) into the part
        result = (
            base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(slot_len, slot_wid)
            .extrude(-slot_dep, combine="cut")
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00997580/gpt_generated.stl')
