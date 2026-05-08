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
        # Parameters
        cyl_d = 40.0
        cyl_r = cyl_d / 2.0
        cyl_h = 60.0
    
        # Cut parameters: remove top quarter of height, and a quarter of the diameter in plan
        cut_h = cyl_h * 0.25
        z0 = cyl_h - cut_h  # start of cut region from bottom
    
        # Base cylinder (bottom at Z=0)
        base = cq.Workplane("XY").cylinder(cyl_h, cyl_r, centered=(True, True, False))
    
        # Cutting box: occupies +X,+Y quadrant (half diameter each direction), only in top quarter of height
        cutter = (
            cq.Workplane("XY")
            .box(cyl_r, cyl_r, cut_h, centered=False)  # from (0,0,0) to (+r,+r,+cut_h)
            .translate((0, 0, z0))
        )
    
        result = base.cut(cutter)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00001615/gpt_generated.stl')
