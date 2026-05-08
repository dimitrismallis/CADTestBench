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
        d1 = 0.38527
        h1 = 0.256849
    
        d2 = 0.256849
        h2 = 0.493151
    
        r1 = d1 / 2.0
        r2 = d2 / 2.0
    
        # Cylinder 1: base on XY plane (Z=0), extends upward
        cyl1 = cq.Workplane("XY").cylinder(h1, r1, centered=(True, True, False))
    
        # Cylinder 2: connected to the center of cylinder 1's base, extends downward from Z=0
        cyl2 = (
            cq.Workplane("XY")
            .cylinder(h2, r2, centered=(True, True, False))
            .translate((0, 0, -h2))
        )
    
        return cyl1.union(cyl2)
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00005161/gpt_generated.stl')
