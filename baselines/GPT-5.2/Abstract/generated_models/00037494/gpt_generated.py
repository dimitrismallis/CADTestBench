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
        # Parameters
        outer_side = 40.0     # outer square side length
        wall = 3.0            # wall thickness
        length_y = 80.0       # extrusion length along Y
    
        inner_side = outer_side - 2 * wall
        if inner_side <= 0:
            raise ValueError("Wall thickness too large; inner_side must be > 0")
    
        # Outer solid: sketch on XZ plane, extrude along +Y
        outer = cq.Workplane("XZ").rect(outer_side, outer_side).extrude(length_y)
    
        # Inner cut: sketch on same XZ plane, centered, cut by extruding along -Y
        # Use combine="cut" so the negative extrusion removes material from the outer solid.
        pipe = (
            outer
            .workplane()  # returns to the same XZ plane at the original origin
            .rect(inner_side, inner_side)
            .extrude(-length_y, combine="cut")
        )
    
        return pipe
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00037494/gpt_generated.stl')
