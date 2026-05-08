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
        # Scalene, obtuse triangle defined by 3 points (mm)
        # A is obtuse because (B-A)·(C-A) < 0
        A = (0.0, 0.0)
        B = (60.0, 0.0)
        C = (20.0, 25.0)
    
        thickness = 5.0  # 3D extrusion thickness
    
        tri = (
            cq.Workplane("XY")
            .moveTo(*A)
            .lineTo(*B)
            .lineTo(*C)
            .close()
            .extrude(thickness)
        )
    
        return tri
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00005721/gpt_generated.stl')
