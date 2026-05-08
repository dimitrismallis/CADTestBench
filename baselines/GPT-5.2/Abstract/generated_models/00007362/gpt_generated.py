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
        # Dimensions (mm): very long (X), wide (Y), short (Z)
        length = 300.0  # X
        width  = 60.0   # Y
        height = 12.0   # Z
    
        result = cq.Workplane("XY").box(length, width, height, centered=True)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00007362/gpt_generated.stl')
