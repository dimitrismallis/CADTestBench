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
        # --- Parameters (units as given) ---
        cyl_height = 0.325804
        cyl_diam   = 0.651607
        cyl_rad    = cyl_diam / 2.0
    
        block_width  = 0.201998   # narrow (Y direction)
        block_height = 0.065161   # very short (Z direction)
        block_length = 0.839006   # longer than cylinder diameter (X direction)
    
        # Placement tuning ("margins and translations")
        z_raise = 0.01  # slight lift above the cylinder top
        # Shift the block so it extrudes outward from one sector of the curved surface (+X side)
        # Keep it still overlapping the cylinder a bit for a clean union.
        overlap = 0.03
        x_shift = cyl_rad - overlap + block_length / 2.0
    
        # --- Base cylinder (axis along Z) ---
        base = cq.Workplane("XY").cylinder(cyl_height, cyl_rad)
    
        # --- Rectangular block (tab) ---
        # Create as a separate solid centered at origin, then translate into position.
        tab = (
            cq.Workplane("XY")
            .box(block_length, block_width, block_height, centered=True)
            .translate((x_shift, 0, cyl_height / 2.0 + block_height / 2.0 + z_raise))
        )
    
        # --- Combine ---
        result = base.union(tab)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00689273/gpt_generated.stl')
