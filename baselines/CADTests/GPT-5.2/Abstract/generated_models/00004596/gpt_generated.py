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
        outer_radius = 20.0
        inner_radius = 3.0   # small inner radius
        height = 200.0       # long cylinder
    
        # Outer solid
        outer = cq.Workplane("XY").cylinder(height, outer_radius)
    
        # Inner cut (make slightly longer to guarantee through cut)
        inner = cq.Workplane("XY").cylinder(height + 2.0, inner_radius)
    
        tube = outer.cut(inner)
        return tube
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00004596/gpt_generated.stl')
