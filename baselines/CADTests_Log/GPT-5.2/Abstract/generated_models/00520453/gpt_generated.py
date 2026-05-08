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
        base_len = 120.0     # "long" base
        tri_height = 30.0    # height of the isosceles triangle
        extrude_h = 20.0     # extrusion height
    
        # Triangle vertices (centered on X=0)
        p1 = (-base_len / 2.0, 0.0)
        p2 = ( base_len / 2.0, 0.0)
        p3 = (0.0, tri_height)
    
        result = (
            cq.Workplane("XY")
            .moveTo(*p1)
            .lineTo(*p2)
            .lineTo(*p3)
            .close()
            .extrude(extrude_h)
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00520453/gpt_generated.stl')
