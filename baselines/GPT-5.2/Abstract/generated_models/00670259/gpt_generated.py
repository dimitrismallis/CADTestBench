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
        length = 200.0          # pipe length along Z
        outer_w = 40.0          # outer width (X)
        outer_h = 20.0          # outer height (Y)
        wall = 2.0              # wall thickness
    
        # Derived inner dimensions
        inner_w = outer_w - 2 * wall
        inner_h = outer_h - 2 * wall
        if inner_w <= 0 or inner_h <= 0:
            raise ValueError("Wall thickness too large for given outer dimensions.")
    
        # --- Model ---
        pipe = (
            cq.Workplane("XY")
            .rect(outer_w, outer_h)
            .extrude(length)
            .faces(">Z").workplane()
            .rect(inner_w, inner_h)
            .cutThruAll()
        )
    
        return pipe
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00670259/gpt_generated.stl')
