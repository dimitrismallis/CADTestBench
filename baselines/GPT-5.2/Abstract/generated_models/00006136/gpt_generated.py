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
        base = 60.0
        height = 40.0
        thickness = 20.0
    
        # Right triangle with vertices at (0,0), (base,0), (0,height)
        tri = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(base, 0)
            .lineTo(0, height)
            .close()
            .extrude(thickness)
        )
    
        return tri
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00006136/gpt_generated.stl')
