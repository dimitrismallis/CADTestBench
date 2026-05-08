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
        side = 1.00328
        height = 0.271665
    
        rot_z_deg = 22.4
        rot_x_deg = -90.0
    
        tx, ty, tz = (-0.176576, 0.0, 0.286546)
    
        # Regular n-gon: side s relates to circumradius R by s = 2*R*sin(pi/n)
        n = 8
        R = side / (2.0 * math.sin(math.pi / n))
    
        # Build octagon and extrude
        solid = (
            cq.Workplane("XY")
            .polygon(n, 2.0 * R)   # polygon takes circumscribed circle diameter
            .extrude(height)
        )
    
        # Apply transforms: rotate about Z, then about X, then translate
        solid = (
            solid
            .rotate((0, 0, 0), (0, 0, 1), rot_z_deg)
            .rotate((0, 0, 0), (1, 0, 0), rot_x_deg)
            .translate((tx, ty, tz))
        )
    
        return solid
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00670441/gpt_generated.stl')
