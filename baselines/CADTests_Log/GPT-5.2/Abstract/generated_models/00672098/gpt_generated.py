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
        outer_w = 60.0     # overall width (X)
        outer_h = 50.0     # overall height (Y)
        wall = 8.0         # wall thickness
        thickness = 6.0    # extrusion thickness (Z)
    
        # Inner cutout dimensions: leave side walls and bottom wall, open at the top
        inner_w = outer_w - 2 * wall
        inner_h = outer_h - wall  # leaves a bottom wall of 'wall' thickness
    
        u_shape = (
            cq.Workplane("XY")
            .rect(outer_w, outer_h)
            .rect(inner_w, inner_h)   # second rect becomes an inner wire
            .extrude(thickness)       # extrude the face with a hole -> U-shaped solid
        )
    
        return u_shape
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00672098/gpt_generated.stl')
