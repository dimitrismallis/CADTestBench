import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    
    def rounded_square_sketch(size: float, corner_r: float) -> cq.Sketch:
        # Clamp radius to valid range
        r = max(0.0, min(corner_r, size / 2.0 - 1e-3))
        sk = cq.Sketch().rect(size, size)
        if r > 0:
            sk = sk.vertices().fillet(r)
        return sk
    
    def create_cad() -> cq.Workplane:
        # --- Parameters (mm) ---
        outer_size = 120.0
        outer_r = 12.0
        height = 40.0
    
        wall = 6.0
        inner_r = 8.0
        inner_size = outer_size - 2.0 * wall
        if inner_size <= 0:
            raise ValueError("wall too large for given outer_size")
    
        # --- Outer body ---
        outer_sk = rounded_square_sketch(outer_size, outer_r)
        body = cq.Workplane("XY").placeSketch(outer_sk).extrude(height)
    
        # --- Inner cavity cut (same depth as body height) ---
        inner_sk = rounded_square_sketch(inner_size, inner_r)
        result = (
            body
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .placeSketch(inner_sk)
            .cutBlind(-height)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00997753/gpt_generated.stl')
