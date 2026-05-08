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
        width = 0.333333          # extrusion thickness (Z)
        height = 0.083333         # leg thickness in 2D sketch
        length = 0.666667         # overall outer size in 2D (0.75 - height)
    
        inner_size = length - height
    
        # Outer square is centered at origin.
        # Inner square cutout has its lower-left corner at (height, height) in outer's local coords.
        # Convert that to a center position relative to origin:
        inner_center_shift = (height + inner_size / 2) - (length / 2)
    
        l_sketch = (
            cq.Sketch()
            .rect(length, length)  # outer
            .push([(inner_center_shift, inner_center_shift)])
            .rect(inner_size, inner_size, mode="s")  # subtract inner
        )
    
        bracket = cq.Workplane("XY").placeSketch(l_sketch).extrude(width)
        return bracket
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00996329/gpt_generated.stl')
