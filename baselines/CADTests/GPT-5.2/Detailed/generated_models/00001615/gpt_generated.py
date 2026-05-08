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
        # Parameters (units as given)
        cyl_h = 1.5
        cyl_d = 0.6
        cyl_r = cyl_d / 2
    
        cut_len = 0.235   # ~1/4 of diameter
        cut_w   = 0.6     # equal to cylinder diameter
        cut_h   = 0.292   # ~1/5 of height
    
        # Base cylinder centered at origin (extends from z=-cyl_h/2 to +cyl_h/2)
        base = cq.Workplane("XY").cylinder(cyl_h, cyl_r)
    
        # Cutter box:
        # - centered in X/Y at cylinder center
        # - its TOP face coincident with cylinder top (z=+cyl_h/2)
        #   so its center is at z=+cyl_h/2 - cut_h/2
        cutter_center_z = (cyl_h / 2) - (cut_h / 2)
    
        cutter = (
            cq.Workplane("XY")
            .center(0, 0)
            .workplane(offset=cutter_center_z)
            .box(cut_len, cut_w, cut_h, centered=True)
        )
    
        result = base.cut(cutter)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00001615/gpt_generated.stl')
