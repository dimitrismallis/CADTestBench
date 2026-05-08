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
        outer_radius = 25.0
        inner_radius = 15.0
        height = 10.0
    
        # Annulus profile: outer circle minus inner circle, then extrude
        result = (
            cq.Workplane("XY")
            .circle(outer_radius)
            .circle(inner_radius)
            .extrude(height)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00003801/gpt_generated.stl')
