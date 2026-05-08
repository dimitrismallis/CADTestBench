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
        # Side-profile widths (X direction)
        w1, w2, w3 = 80.0, 55.0, 30.0
        # Step heights (Z direction)
        h1, h2, h3 = 20.0, 15.0, 10.0
        # Extrusion depth (Y direction)
        depth = 50.0
    
        # Build a closed "stair-step" profile in the XZ plane, centered about X=0.
        # Coordinates are (x, z) in that plane.
        x1, x2, x3 = w1 / 2.0, w2 / 2.0, w3 / 2.0
        z0, z1, z2, z3 = 0.0, h1, h1 + h2, h1 + h2 + h3
    
        pts = [
            (-x1, z0),
            ( x1, z0),
            ( x1, z1),
            ( x2, z1),
            ( x2, z2),
            ( x3, z2),
            ( x3, z3),
            (-x3, z3),
            (-x3, z2),
            (-x2, z2),
            (-x2, z1),
            (-x1, z1),
        ]
    
        pedestal = (
            cq.Workplane("XZ")
            .polyline(pts)
            .close()
            .extrude(depth, both=True)  # extrude symmetrically about the XZ plane (along Y)
        )
    
        return pedestal
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00682075/gpt_generated.stl')
