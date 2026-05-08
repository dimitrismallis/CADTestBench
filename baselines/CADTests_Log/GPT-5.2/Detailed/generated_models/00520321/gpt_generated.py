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
        L = 1.23418
        W = 0.617188
        H = 0.75
    
        cyl_h = 0.140625
        cyl_d = 0.380469
        cyl_r = cyl_d / 2.0
    
        pad_from_length_edges = 0.118359  # padding from the +/-X edges of the prism
    
        # Cylinder center offset from origin along X:
        # edge-to-cylinder-outer = pad => (L/2) - (|x| + r) = pad  => |x| = L/2 - pad - r
        x_off = (L / 2.0) - pad_from_length_edges - cyl_r
    
        # --- Main brick ---
        brick = cq.Workplane("XY").box(L, W, H, centered=True)
    
        # --- Two bottom cylinders (protruding downward) ---
        # Put cylinder bases on the bottom face and extrude downward (negative Z)
        cylinders = (
            cq.Workplane("XY")
            .workplane(offset=-H / 2.0)  # bottom face plane (z = -H/2)
            .pushPoints([(x_off, 0.0), (-x_off, 0.0)])
            .circle(cyl_r)
            .extrude(-cyl_h)  # downwards
        )
    
        result = brick.union(cylinders)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00520321/gpt_generated.stl')
