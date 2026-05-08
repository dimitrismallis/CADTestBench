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
        height = 300.0          # very long
        inner_radius = 20.0     # medium sized inner radius
        wall_thickness = 3.0
        outer_radius = inner_radius + wall_thickness
    
        outer = cq.Workplane("XY").cylinder(height, outer_radius)
        inner = cq.Workplane("XY").cylinder(height + 2.0, inner_radius)  # slightly longer to ensure clean cut
    
        hollow_cylinder = outer.cut(inner)
        return hollow_cylinder
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00008138/gpt_generated.stl')
