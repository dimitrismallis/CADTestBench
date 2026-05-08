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
        base_radius = 20.0
        base_height = 10.0
    
        hole_d = 3.0
        hole_square = 20.0  # center-to-center spacing in X and Y (square)
    
        # --- Model ---
        result = (
            cq.Workplane("XY")
            .circle(base_radius)
            .extrude(base_height)
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .rect(hole_square, hole_square, forConstruction=True)
            .vertices()
            .hole(hole_d)  # through-hole
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00034243/gpt_generated.stl')
