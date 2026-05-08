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
        diameter = 200.0   # very large diameter
        height = 10.0      # short cylinder
        radius = diameter / 2.0
    
        result = cq.Workplane("XY").circle(radius).extrude(height)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00670106/gpt_generated.stl')
