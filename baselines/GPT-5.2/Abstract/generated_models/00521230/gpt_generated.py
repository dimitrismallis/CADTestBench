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
        # --- Parameters ---
        cyl_d = 12.0
        cyl_r = cyl_d / 2.0
        cyl_h = 120.0
    
        hole_d = cyl_d * 0.85          # slightly smaller than cylinder diameter
        hole_r = hole_d / 2.0
        hole_len = cyl_d * 3.0         # long enough to cut through the cylinder
    
        # Z positions
        z_top = cyl_h * 0.35           # near top (cylinder is centered at Z=0)
        z_bot1 = -cyl_h * 0.35         # near bottom
        z_bot2 = -cyl_h * 0.25         # also near bottom, but a bit higher
    
        # Radial offsets (Y direction). One bottom hole closer to center.
        y_top = cyl_r * 0.55
        y_bot_far = cyl_r * 0.55
        y_bot_close = cyl_r * 0.30     # closer to center
    
        # --- Base cylinder (axis along Z) ---
        base = cq.Workplane("XY").cylinder(cyl_h, cyl_r)
    
        # --- Helper: make a radial hole (axis along X) at given (y,z) ---
        def radial_hole(y, z):
            return (
                cq.Workplane("YZ", origin=(0, y, z))
                .circle(hole_r)
                .extrude(hole_len, both=True)
            )
    
        holes = (
            radial_hole(y_top, z_top)
            .union(radial_hole(y_bot_far, z_bot1))
            .union(radial_hole(y_bot_close, z_bot2))
        )
    
        result = base.cut(holes)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00521230/gpt_generated.stl')
