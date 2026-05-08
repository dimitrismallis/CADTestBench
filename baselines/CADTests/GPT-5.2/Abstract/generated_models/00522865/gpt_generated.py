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
        base_L = 80.0
        base_W = 50.0
        base_H = 8.0  # "slightly extrude"
    
        pocket_scale = 0.5
        pocket_depth = base_H * 0.6  # hollow pocket depth (not thru)
    
        top_scale = 0.75
        top_H = base_H * 0.25  # 1/4th the extrusion of the original
    
        # tiny rectangles on top
        tiny_L = base_L * 0.10
        tiny_W = base_W * 0.08
        tiny_H = base_H * 0.20  # small extrusion
    
        # Position: either side of first line of symmetry (X axis => left/right),
        # slightly below second line of symmetry (Y axis => negative Y).
        x_off = (base_L * top_scale) * 0.22
        y_off = -(base_W * top_scale) * 0.12
    
        # --- Model ---
        result = (
            cq.Workplane("XY")
            # Base plate
            .rect(base_L, base_W)
            .extrude(base_H)
    
            # Center rectangular hollow (half size)
            .faces(">Z").workplane()
            .rect(base_L * pocket_scale, base_W * pocket_scale)
            .cutBlind(-pocket_depth)
    
            # Top pad (3/4 size, 1/4 height), centered on top
            .faces(">Z").workplane()
            .rect(base_L * top_scale, base_W * top_scale)
            .extrude(top_H)
    
            # Two tiny rectangles on top pad
            .faces(">Z").workplane()
            .pushPoints([(x_off, y_off), (-x_off, y_off)])
            .rect(tiny_L, tiny_W)
            .extrude(tiny_H)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00522865/gpt_generated.stl')
