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
        cyl_d = 60.0
        cyl_h = 12.0
    
        prism_len = 70.0          # slightly longer than cylinder diameter
        prism_w   = 12.0          # narrow
        prism_h   = 8.0           # short
    
        # Base cylinder (short, large diameter)
        base = cq.Workplane("XY").cylinder(cyl_h, cyl_d / 2.0)
    
        # Rectangular prism sitting horizontally on top of the cylinder
        top_prism = (
            cq.Workplane("XY", origin=(0, 0, cyl_h + prism_h / 2.0))
            .box(prism_len, prism_w, prism_h, centered=True)
        )
    
        return base.union(top_prism)
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00019015/gpt_generated.stl')
