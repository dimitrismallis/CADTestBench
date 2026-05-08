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
        # Parameters
        side = 40.0      # approximate size of triangle
        height = 20.0    # extrusion height
    
        # Define triangle vertices (2D) on XY plane
        p1 = (0, 0)
        p2 = (side, 0)
        p3 = (side * 0.5, side * math.sqrt(3) / 2.0)  # equilateral triangle apex
    
        result = (
            cq.Workplane("XY")
            .moveTo(*p1)
            .lineTo(*p2)
            .lineTo(*p3)
            .close()
            .extrude(height)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00001977/gpt_generated.stl')
