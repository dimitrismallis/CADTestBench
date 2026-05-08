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
        # --- Given dimensions (units as provided) ---
        total_h = 0.56371
    
        h1 = 0.242143  # first half height
        h2 = 0.321568  # second half height
    
        id1 = 0.332143  # smaller hole diameter
        id2 = 0.728571  # larger hole diameter
    
        # Choose an outer diameter that safely exceeds the larger ID (adds wall thickness)
        wall = 0.10
        od = id2 + 2 * wall
    
        # --- Model ---
        # Outer body
        part = cq.Workplane("XY").cylinder(total_h, od / 2)
    
        # Cut smaller bore from bottom up to h1
        part = (
            part.faces("<Z")
            .workplane(centerOption="CenterOfMass")
            .hole(id1, depth=h1)
        )
    
        # Cut larger bore from top down to h2
        part = (
            part.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .hole(id2, depth=h2)
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00039681/gpt_generated.stl')
