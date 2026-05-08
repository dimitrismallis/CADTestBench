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
        r1 = 30.0   # big cylinder radius
        h1 = 20.0   # big cylinder height
    
        r2 = 25.0   # smaller radius
        h2 = 35.0   # taller height
    
        # Big cylinder: base on XY plane at z=0, extends to +Z
        big_cyl = cq.Workplane("XY").circle(r1).extrude(h1)
    
        # Second cylinder: centered on same axis, base coincident with big cylinder base center
        small_tall_cyl = cq.Workplane("XY").circle(r2).extrude(h2)
    
        # Union them (connected at the base center)
        result = big_cyl.union(small_tall_cyl)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00005161/gpt_generated.stl')
