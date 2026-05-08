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
        cyl_d = 30.0          # wide cylinder diameter
        cyl_h = 12.0          # short cylinder height
    
        block_len = 40.0      # longer than cylinder diameter
        block_w   = 8.0       # narrow (along Y)
        block_h   = 4.0       # very short (along Z)
    
        # Place the block so it protrudes from the curved surface near the top.
        # Cylinder is centered at origin: Z spans [-cyl_h/2, +cyl_h/2]
        z_top = cyl_h / 2.0
        r = cyl_d / 2.0
    
        # Block is tangent to cylinder at +X side; its inner face touches x = r
        block_center_x = r + block_len / 2.0
        block_center_z = z_top - block_h / 2.0  # sit on the top surface
    
        # --- Model ---
        base = cq.Workplane("XY").cylinder(cyl_h, cyl_d / 2.0)
    
        block = (
            cq.Workplane("XY")
            .box(block_len, block_w, block_h, centered=True)
            .translate((block_center_x, 0.0, block_center_z))
        )
    
        result = base.union(block)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00689273/gpt_generated.stl')
