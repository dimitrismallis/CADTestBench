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
        stem_h = 80.0                 # long vertical rectangle height
        width = 16.0                  # common width for both rectangles
        cap_h = stem_h * 0.25         # ~1/4 of stem height
        thickness = 6.0               # small extrusion amount
    
        # Cap placed near the top of the stem
        top_margin = 6.0
        cap_center_y = stem_h / 2 - cap_h / 2 - top_margin
    
        # Skew (shear): x' = x + k*y
        shear_k = 0.18
    
        # --- Build as two extrusions and union (simple + reliable) ---
        stem = cq.Workplane("XY").rect(width, stem_h).extrude(thickness)
    
        cap = (
            cq.Workplane("XY")
            .center(0, cap_center_y)
            .rect(width, cap_h)
            .extrude(thickness)
        )
    
        t_solid = stem.union(cap)
    
        # --- Apply skew transform to the resulting solid ---
        trsf = cq.Matrix(
            [
                [1.0, shear_k, 0.0, 0.0],
                [0.0, 1.0,     0.0, 0.0],
                [0.0, 0.0,     1.0, 0.0],
            ]
        )
    
        skewed = t_solid.newObject([t_solid.val().transformGeometry(trsf)])
        return skewed
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00998300/gpt_generated.stl')
