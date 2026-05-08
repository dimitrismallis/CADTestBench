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
        # --- Irregular pentagon parameters (mm) ---
        # Define points CCW; bottom edge is p0->p1 and is intentionally the shortest.
        p0 = (-8.0, 0.0)
        p1 = ( 8.0, 0.0)   # bottom edge length = 16 (shortest)
        p2 = (22.0, 18.0)
        p3 = ( 6.0, 42.0)
        p4 = (-18.0, 26.0)
    
        pts = [p0, p1, p2, p3, p4]
    
        # Pentagon "height" as vertical span in Y
        ys = [p[1] for p in pts]
        pent_height = max(ys) - min(ys)  # here: 42 - 0 = 42
    
        # Extrude almost 2x the height
        extrude_h = 1.9 * pent_height  # ~2x
    
        # --- Build ---
        wp = cq.Workplane("XY")
        pent = (
            wp.moveTo(*pts[0])
            .lineTo(*pts[1])
            .lineTo(*pts[2])
            .lineTo(*pts[3])
            .lineTo(*pts[4])
            .close()
        )
    
        result = pent.extrude(extrude_h)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00998398/gpt_generated.stl')
