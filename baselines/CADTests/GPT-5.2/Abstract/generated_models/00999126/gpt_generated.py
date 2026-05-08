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
        h = 20.0                 # rectangle height
        w = 3.0 * h              # rectangle width (3x height)
        depth = 4.0              # small extrusion depth
    
        # Cutout parameters
        cutout_height = 8.0      # vertical size of each cutout
        right_len = 6.0          # horizontal length of right cutout (into the part)
        left_len = 3.0 * right_len  # left cutout is 3x longer than right
    
        # Centers of cutouts on left/right edges (centered vertically)
        left_center_x = -w / 2.0 + left_len / 2.0
        right_center_x = w / 2.0 - right_len / 2.0
    
        # --- Build 2D sketch and extrude ---
        result = (
            cq.Workplane("XY")
            .rect(w, h)
            # subtract left cutout
            .center(left_center_x, 0)
            .rect(left_len, cutout_height, forConstruction=False)
            # subtract right cutout
            .center(-left_center_x + right_center_x, 0)  # move from left cutout center to right cutout center
            .rect(right_len, cutout_height, forConstruction=False)
            # cut the two rectangles from the base rectangle
            .extrude(depth)
        )
    
        # The above created overlapping wires; to ensure they are cutouts, use a sketch boolean approach:
        # Rebuild robustly using Sketch API (more explicit subtract)
        base = cq.Sketch().rect(w, h)
        cuts = (
            cq.Sketch()
            .rect(left_len, cutout_height).moved(cq.Location(cq.Vector(left_center_x, 0, 0)))
            .rect(right_len, cutout_height, mode="a").moved(cq.Location(cq.Vector(right_center_x, 0, 0)))
        )
        face = base.face(cuts, mode="s")
        final_result = cq.Workplane("XY").placeSketch(face).extrude(depth)
    
        return final_result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00999126/gpt_generated.stl')
