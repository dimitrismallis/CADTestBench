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
        length = 0.668421   # X dimension
        width  = 0.334211   # Y dimension
        height = 0.668421   # Z extrusion
    
        circle_d = 0.2625
        circle_r = circle_d / 2.0
    
        # Base block (centered on origin)
        block = cq.Workplane("XY").box(length, width, height, centered=True)
    
        # Top-right corner of the rectangle in XY (for a centered rectangle)
        corner_x = length / 2.0
        corner_y = width / 2.0
    
        # Create the cutting cylinder starting at Z = -height/2 and extruding +Z by height
        # so it fully spans the block.
        cut_cyl = (
            cq.Workplane("XY", origin=(0, 0, -height / 2.0))
            .center(corner_x, corner_y)
            .circle(circle_r)
            .extrude(height)
        )
    
        result = block.cut(cut_cyl)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00685823/gpt_generated.stl')
