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
        # Dimensions (units as provided by the prompt)
        length = 0.75
        width  = 0.06429
        height = 0.03929
    
        # box() is centered at the workplane origin by default (centered=True)
        result = cq.Workplane("XY").box(length, width, height)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00007362/gpt_generated.stl')
