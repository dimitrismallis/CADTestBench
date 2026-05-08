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
        outer_d = 40.0
        inner_d = 24.0
        extrude_y = 15.0
    
        # Build ring profile on XZ plane and extrude along +Y
        ring = (
            cq.Workplane("XZ")
            .circle(outer_d / 2.0)
            .circle(inner_d / 2.0)
            .extrude(extrude_y)
        )
    
        return ring
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00670279/gpt_generated.stl')
