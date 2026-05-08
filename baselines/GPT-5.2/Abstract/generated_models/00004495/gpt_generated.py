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
        inner_radius = 15.0
        height = 40.0
    
        # Outer solid cylinder
        outer = cq.Workplane("XY").cylinder(height, outer_radius)
    
        # Inner cylinder used as a cutting tool (slightly taller to guarantee through cut)
        inner = cq.Workplane("XY").cylinder(height + 2.0, inner_radius)
    
        # Hollow cylinder (tube)
        result = outer.cut(inner)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00004495/gpt_generated.stl')
