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
        # Parameters (all in mm)
        length = 80.0   # shared long edge length
        width  = 40.0   # extent away from the shared edge
        height = 3.0    # marginal extrusion thickness
    
        # "Floor" plate: thin prism, long edge along X, width along Y, thickness along Z
        floor = cq.Workplane("XY").box(length, width, height, centered=True)
    
        # "Wall" plate: identical prism, rotated to stand up (thickness becomes Y, width becomes Z)
        wall = (
            cq.Workplane("XY")
            .box(length, width, height, centered=True)
            .rotate((0, 0, 0), (1, 0, 0), 90)          # rotate around X axis
            .translate((0, -height/2, width/2))        # align to share the long edge with the floor
        )
    
        # Union to form the corner
        result = floor.union(wall)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00002221/gpt_generated.stl')
