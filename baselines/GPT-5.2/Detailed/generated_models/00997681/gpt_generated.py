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
        length = 0.058594
        width = 0.75
        height = 0.216797
    
        r_req = height - 0.1875
    
        # Fillet radius must fit within the rectangle; clamp to avoid OCCT failure
        r_max = 0.499 * min(length, width)  # slightly under half to be robust
        fillet_r = min(r_req, r_max)
    
        # Build 2D face with two filleted corners on the +Y long edge using Sketch API
        sk = (
            cq.Sketch()
            .rect(length, width)
            .vertices(">Y")
            .fillet(fillet_r)
        )
    
        result = cq.Workplane("XY").placeSketch(sk).extrude(height)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00997681/gpt_generated.stl')
