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
        outer_d = 80.0   # large diameter
        height  = 20.0   # smaller than diameter
        cutout_d = 12.0  # small central cutout
    
        result = (
            cq.Workplane("XY")
            .cylinder(height, outer_d / 2.0)
            .faces(">Z").workplane()
            .circle(cutout_d / 2.0)
            .cutThruAll()
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00001490/gpt_generated.stl')
