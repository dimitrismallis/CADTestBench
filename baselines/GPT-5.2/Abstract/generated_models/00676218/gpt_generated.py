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
        base_side = 40.0
        top_side = 34.0
        tier_height = 3.0
    
        # Base square, marginally extruded
        result = cq.Workplane("XY").rect(base_side, base_side).extrude(tier_height)
    
        # Smaller square on top, same center, extruded by same amount
        result = (
            result
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(top_side, top_side)
            .extrude(tier_height)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00676218/gpt_generated.stl')
