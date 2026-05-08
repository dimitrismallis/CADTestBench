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
        # Parameters (units as given)
        length = 0.475652
        width_base = 0.049547
        width_top = 0.198188
        height = 0.317101
    
        # Base tier
        result = (
            cq.Workplane("XY")
            .rect(length, width_base)
            .extrude(height)
        )
    
        # Top tier (centered on the same origin, extruded from the top face)
        result = (
            result
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(length, width_top)
            .extrude(height)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00984833/gpt_generated.stl')
