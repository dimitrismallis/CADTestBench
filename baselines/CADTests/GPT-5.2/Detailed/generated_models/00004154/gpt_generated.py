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
        # Parameters (units as given)
        length = 0.70588
        width  = 0.40809
        height = 0.22059
        fillet_r = 0.08
    
        # Box is centered at origin by default; then fillet vertical edges only.
        part = (
            cq.Workplane("XY")
            .box(length, width, height, centered=True)
            .edges("|Z")
            .fillet(fillet_r)
        )
    
        # Move so base is on Z=0 and base center is at (0,0,0)
        part = part.translate((0, 0, height / 2.0))
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00004154/gpt_generated.stl')
