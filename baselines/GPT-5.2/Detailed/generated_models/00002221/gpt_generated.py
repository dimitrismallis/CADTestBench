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
        # Dimensions (units as given in prompt)
        length = 0.0625   # short side
        width  = 0.75     # long side (edge to connect along)
        height = 0.0034   # thickness
    
        # Plate 1: "floor" on XY plane, thickness in +Z
        floor = cq.Workplane("XY").box(length, width, height, centered=False)
    
        # Plate 2: "wall" on YZ plane, thickness in +X
        # Dimensions on YZ: Y=width (long), Z=length (short), X=height (thickness)
        wall = cq.Workplane("YZ").box(width, length, height, centered=False)
    
        # Union: they meet along the shared long edge at X=0, Z=0, Y in [0, width]
        result = floor.union(wall)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00002221/gpt_generated.stl')
