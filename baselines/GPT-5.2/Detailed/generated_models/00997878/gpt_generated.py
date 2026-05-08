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
        outer_len = 0.448905
        outer_wid = 0.75
        depth = 0.136861
    
        hole_len = 0.328467
        hole_wid = 0.229927
        gap_between_holes = 0.104015  # clear space between the two holes (along length direction)
    
        # Rounded corner radius for holes (reasonable relative to hole size)
        hole_corner_r = min(hole_len, hole_wid) * 0.15
    
        # Hole center offsets along X so that the gap between inner edges is as specified
        center_to_center = hole_len + gap_between_holes
        x_off = center_to_center / 2.0
    
        # --- Base block ---
        block = cq.Workplane("XY").box(outer_len, outer_wid, depth, centered=(True, True, False))
    
        # --- Hole sketch (rounded rectangle) ---
        hole_sk = (
            cq.Sketch()
            .rect(hole_len, hole_wid)
            .vertices()
            .fillet(hole_corner_r)
        )
    
        # --- Cut two symmetric holes through all ---
        result = (
            block.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .placeSketch(
                hole_sk.moved(x=-x_off, y=0),
                hole_sk.moved(x= x_off, y=0),
            )
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00997878/gpt_generated.stl')
