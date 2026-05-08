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
        length = 80.0
        width = 50.0
        thickness = 10.0
        corner_radius = 8.0
    
        # Extrude a rectangle, then fillet the vertical edges to round the corners
        result = (
            cq.Workplane("XY")
            .rect(length, width)
            .extrude(thickness)
            .edges("|Z")              # vertical edges (the 4 corner edges)
            .fillet(corner_radius)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00681463/gpt_generated.stl')
