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
        bulb_r = 10.0
    
        stem_w = 6.0
        stem_h = 7.0 * stem_w  # height about 7x width
    
        # Small overlap so the rectangle touches the circle but doesn't fully merge into it
        overlap = 1.0
    
        hole_r = 1.2
        hole_edge_margin = 4.0  # distance down from top edge of stem
    
        thickness = 3.0  # extrusion depth
    
        # --- 2D sketch (closed area) ---
        # Bulb centered at origin
        # Stem placed above bulb with slight overlap
        stem_center_y = (bulb_r - overlap) + stem_h / 2.0
    
        sk = (
            cq.Sketch()
            .circle(bulb_r)  # bulb
            .push([(0.0, stem_center_y)])
            .rect(stem_w, stem_h, mode="a")  # stem (add)
        )
    
        # Extrude the closed sketch to 3D
        body = cq.Workplane("XY").placeSketch(sk).extrude(thickness)
    
        # --- Hole near top of stem ---
        hole_center_y = (bulb_r - overlap) + stem_h - hole_edge_margin
        body = (
            body.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .center(0.0, hole_center_y)
            .hole(2.0 * hole_r)
        )
    
        return body
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00998074/gpt_generated.stl')
