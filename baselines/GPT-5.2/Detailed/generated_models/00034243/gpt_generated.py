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
        main_d = 1.5
        main_r = main_d / 2.0
        height = 0.1
    
        hole_d = 0.1124
        hole_r = hole_d / 2.0
    
        padding = 0.041187
    
        # Offset from center for square hole pattern (per prompt)
        offset = (main_r / 2.0) - hole_r - padding
    
        # --- Base solid ---
        part = cq.Workplane("XY").circle(main_r).extrude(height)
    
        # --- Holes: square layout, symmetric about center ---
        hole_pts = [
            ( offset,  offset),
            ( offset, -offset),
            (-offset,  offset),
            (-offset, -offset),
        ]
    
        part = (
            part.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .pushPoints(hole_pts)
            .hole(hole_d)  # through-hole (default depth=None => thru all)
        )
    
        # --- Rotate square of holes diagonally relative to cylinder (about Z) ---
        part = part.rotate((0, 0, 0), (0, 0, 1), 45)
    
        # --- Rotate part 90 degrees about Y-axis ---
        part = part.rotate((0, 0, 0), (0, 1, 0), 90)
    
        # --- Center in 3D space by translating bounding-box center to origin ---
        bb = part.val().BoundingBox()
        cx = (bb.xmin + bb.xmax) / 2.0
        cy = (bb.ymin + bb.ymax) / 2.0
        cz = (bb.zmin + bb.zmax) / 2.0
        part = part.translate((-cx, -cy, -cz))
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00034243/gpt_generated.stl')
