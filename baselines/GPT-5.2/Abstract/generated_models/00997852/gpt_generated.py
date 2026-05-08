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
        base_h   = 12.0
    
        top_len  = 40.0
        top_wid  = 25.0
        top_h    = 10.0
    
        # Base block
        result = (
            cq.Workplane("XY")
            .rect(base_len, base_wid)
            .extrude(base_h)
            # Top tier: sketch on top face, centered, then extrude upward
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(top_len, top_wid)
            .extrude(top_h)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00997852/gpt_generated.stl')
