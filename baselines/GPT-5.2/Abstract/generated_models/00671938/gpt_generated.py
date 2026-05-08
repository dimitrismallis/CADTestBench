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
        r = 12.0          # circle radius
        offset = 10.0     # center-to-center offset (less than 2*r => overlap)
        height = 25.0     # extrusion height
    
        # Two overlapping circles -> one combined profile -> extrude
        result = (
            cq.Workplane("XY")
            .circle(r)
            .center(offset, 0).circle(r)   # second circle overlaps the first
            .extrude(height)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00671938/gpt_generated.stl')
