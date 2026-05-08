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
        r1 = 20.0          # outer cylinder radius
        h1 = 6.0           # outer cylinder extrusion height (slight)
        r2 = 8.0           # inner cylinder radius
        h2 = 10.0          # inner cylinder extrusion height
    
        # notch (rectangle cut) positioned to the right of the inner cylinder
        notch_w = 6.0      # size in X
        notch_h = 10.0     # size in Y
        notch_depth = 3.0  # cut depth into the outer cylinder from the top
        notch_gap = 1.0    # gap between inner cylinder OD and notch start
    
        # Compute notch center X so its left edge is just to the right of inner cylinder
        notch_center_x = (r2 + notch_gap) + notch_w / 2.0
    
        # --- Model ---
        base = cq.Workplane("XY").circle(r1).extrude(h1)
    
        # Second cylinder in the middle of the first, extruded upward from the top face
        boss = base.faces(">Z").workplane(centerOption="CenterOfMass").circle(r2).extrude(h2)
    
        # Cut a small rectangle in the first cylinder (from the top), on the right side of the second cylinder
        result = (
            boss.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .center(notch_center_x, 0)
            .rect(notch_w, notch_h)
            .cutBlind(-notch_depth)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00520671/gpt_generated.stl')
