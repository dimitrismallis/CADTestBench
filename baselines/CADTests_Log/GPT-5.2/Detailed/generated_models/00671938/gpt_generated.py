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
        height = 0.75
        diameter = 0.419231
        radius = diameter / 2.0
    
        p1 = (-0.09259, -0.022198)
        p2 = (0.082574, 0.01872)
    
        # Build two overlapping circles in one sketch (pending wires), then extrude
        result = (
            cq.Workplane("XY")
            .pushPoints([p1, p2])
            .circle(radius)
            .extrude(height)
            # ensure cylinder centers are at z=height/2 (i.e., base at z=0)
            .translate((0, 0, height / 2.0))
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00671938/gpt_generated.stl')
