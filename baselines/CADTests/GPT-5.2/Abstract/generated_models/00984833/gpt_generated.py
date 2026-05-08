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
        length = 80.0
        width_base = 40.0
        width_top = 32.0   # slightly smaller width, same length
        height = 10.0      # both tiers extruded by the same amount
    
        # Base tier
        result = cq.Workplane("XY").rect(length, width_base).extrude(height)
    
        # Top tier (centered automatically on the same origin when using workplane on top face)
        result = (
            result
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .rect(length, width_top)
            .extrude(height)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00984833/gpt_generated.stl')
