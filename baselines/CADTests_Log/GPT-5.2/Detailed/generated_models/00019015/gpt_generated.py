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
        cyl_h = 0.468766
        cyl_d = 1.31858
        cyl_r = cyl_d / 2.0
    
        prism_l = 1.5
        prism_w = 0.1875
        prism_h = 0.075
    
        # Cylinder centered at origin, standing on XY plane (symmetric about Z=0 by default)
        cyl = cq.Workplane("XY").cylinder(cyl_h, cyl_r)
    
        # Rectangular prism centered at origin, then moved so it sits on top of cylinder
        # Cylinder top is at +cyl_h/2, prism bottom should meet that plane:
        z_shift = (cyl_h / 2.0) + (prism_h / 2.0)
        prism = cq.Workplane("XY").box(prism_l, prism_w, prism_h).translate((0, 0, z_shift))
    
        # Union them into one model
        result = cyl.union(prism)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00019015/gpt_generated.stl')
