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
        w = 20.0              # width (Y)
        l = 2.0 * w           # length (X), twice width
        h = 12.0              # height (Z)
    
        # Cylinders: "1/4th the size of the rectangular prism"
        # Interpreted as: diameter = 1/4 of width, height = 1/4 of prism height
        cyl_d = w / 4.0
        cyl_r = cyl_d / 2.0
        cyl_h = h / 4.0
    
        # Symmetric placement along Y, centered in X, attached to bottom face
        y_offset = w / 4.0
    
        # --- Model ---
        base = cq.Workplane("XY").box(l, w, h, centered=True)
    
        studs = (
            cq.Workplane("XY")
            .pushPoints([(0, -y_offset), (0, y_offset)])
            .circle(cyl_r)
            .extrude(cyl_h, combine=False)
            .translate((0, 0, -h / 2.0 - cyl_h / 2.0))  # attach to bottom of base
        )
    
        result = base.union(studs)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00520321/gpt_generated.stl')
