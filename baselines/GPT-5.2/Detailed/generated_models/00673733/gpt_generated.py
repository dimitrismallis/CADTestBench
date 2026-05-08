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
        width = 0.75
        diameter = 0.249945
        radius = diameter / 2.0
        z_shift = 0.125404
    
        cyl1 = cq.Workplane("XY").cylinder(height=width, radius=radius)
        cyl2 = cq.Workplane("XY").cylinder(height=width, radius=radius).translate((0, 0, z_shift))
    
        crescent = cyl1.cut(cyl2)
    
        # Translate by half the width in -Y direction
        result = crescent.translate((0, -width / 2.0, 0))
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00673733/gpt_generated.stl')
