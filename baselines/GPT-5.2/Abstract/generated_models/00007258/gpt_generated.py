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
        # Parameters (mm): long (X), narrow (Y), tall (Z)
        length = 120.0
        width  = 20.0
        height = 60.0
    
        result = cq.Workplane("XY").box(length, width, height, centered=True)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00007258/gpt_generated.stl')
