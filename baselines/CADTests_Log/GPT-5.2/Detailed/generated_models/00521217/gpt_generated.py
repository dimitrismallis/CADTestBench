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
        # Parameters (units as provided)
        d1 = 0.059646
        h1 = 0.750036
    
        d2 = d1 / 2.0
        h2 = h1 * 5.0
    
        r1 = d1 / 2.0
        r2 = d2 / 2.0
    
        # Main (large) cylinder, extruded upward from Z=0
        part = cq.Workplane("XY").circle(r1).extrude(h1)
    
        # Secondary (smaller, longer) cylinder attached to the bottom, extruded downward
        part = part.faces("<Z").workplane(centerOption="CenterOfMass").circle(r2).extrude(-h2)
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00521217/gpt_generated.stl')
