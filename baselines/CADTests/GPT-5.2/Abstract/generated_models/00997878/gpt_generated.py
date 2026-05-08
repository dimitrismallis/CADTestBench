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
        H = 60.0                 # base rectangle height
        W = 2.0 * H              # base rectangle width (twice height)
        depth = H / 4.0          # extrusion depth
    
        hole_w = (5.0 / 12.0) * W
        hole_h = (7.0 / 10.0) * H
    
        # Corner radius for hole rectangles
        fillet_r = 0.12 * min(hole_w, hole_h)
    
        # Hole placement: symmetric about Y axis (vertical centerline in XY sketch)
        side_margin = 0.10 * W
        gap_between_holes = 0.08 * W
    
        # Ensure feasible spacing; otherwise compute equal margins
        if (2 * hole_w + 2 * side_margin + gap_between_holes) > W:
            side_margin = (W - 2 * hole_w) / 3.0
    
        x_center = (W / 2.0) - side_margin - (hole_w / 2.0)
        hole_centers = [(-x_center, 0.0), (x_center, 0.0)]
    
        # --- Sketches ---
        base_sk = cq.Sketch().rect(W, H)
    
        hole_sk = (
            cq.Sketch()
            .rect(hole_w, hole_h)
            .vertices()
            .fillet(fillet_r)
        )
    
        # Place two holes and subtract from base sketch
        sk = base_sk
        for (x, y) in hole_centers:
            sk = sk.face(hole_sk.moved(x=x, y=y), mode="s")
    
        # --- Model ---
        result = cq.Workplane("XY").placeSketch(sk).extrude(depth)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00997878/gpt_generated.stl')
