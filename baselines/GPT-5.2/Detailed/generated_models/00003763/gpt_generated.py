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
        # --- Parameters (units as given) ---
        h1, d1 = 0.248985, 0.192096
        h2, d2 = 0.220645, 0.13302
        h3, d3 = 0.070261, 0.250707
    
        hole_d = 0.098666
        total_h = 0.539891  # given total length
    
        r1, r2, r3 = d1 / 2.0, d2 / 2.0, d3 / 2.0
        hole_r = hole_d / 2.0
    
        # --- Build stacked cylinders (coaxial) ---
        # Cylinder 1: base at Z=0, extends to +h1
        c1 = cq.Workplane("XY").circle(r1).extrude(h1)
    
        # Cylinder 2: sits on top of cylinder 1 (connects to center of c1's top/base interface)
        c2 = cq.Workplane("XY", origin=(0, 0, h1)).circle(r2).extrude(h2)
    
        # Cylinder 3: sits on top of cylinder 2
        c3 = cq.Workplane("XY", origin=(0, 0, h1 + h2)).circle(r3).extrude(h3)
    
        assembly = c1.union(c2).union(c3)
    
        # --- Centered through cut-out spanning entire assembly ---
        # Cut a cylinder from Z=0 through total_h
        hole = cq.Workplane("XY").circle(hole_r).extrude(total_h)
        result = assembly.cut(hole)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00003763/gpt_generated.stl')
