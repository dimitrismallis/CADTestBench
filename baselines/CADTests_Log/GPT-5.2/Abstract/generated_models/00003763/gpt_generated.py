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
        # --- Parameters (mm) ---
        h1 = 30.0
        d1 = 40.0
    
        h2 = h1
        d2 = 20.0  # smaller diameter than first
    
        h3 = 15.0  # shorter height
        d3 = 55.0  # larger diameter than first two
    
        cut_d = 6.0  # small circular cut-out diameter
    
        # --- Model ---
        # Cylinder 1: base, sitting on XY plane (base at Z=0)
        c1 = cq.Workplane("XY").circle(d1 / 2).extrude(h1)
    
        # Cylinder 2: same height as c1, smaller diameter, attached to center of c1 top face
        c2 = (
            c1.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .circle(d2 / 2)
            .extrude(h2)
        )
    
        # Cylinder 3: shorter, larger diameter, attached to center of c2 top face
        c3 = (
            c2.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .circle(d3 / 2)
            .extrude(h3)
        )
    
        total_h = h1 + h2 + h3
    
        # Central cut-out through all three cylinders
        result = (
            c3.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .hole(cut_d, depth=total_h)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00003763/gpt_generated.stl')
