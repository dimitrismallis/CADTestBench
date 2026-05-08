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
        height = 0.103604
        L = 0.725228
    
        y_off = L / 4.0 + 0.0155
    
        # Vertex coordinates as specified (in order around the perimeter)
        pts = [
            (0.0, 0.0),
            (L, 0.0),
            (0.932436, y_off),
            (1.05676, L / 2.0),
            (0.932436, L - y_off),
            (L, L),
            (0.0, L),
        ]
    
        # --- Build profile and extrude ---
        prof = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
        )
    
        solid = prof.extrude(height)
    
        # --- Orientation ---
        # Extrude is along +Z by default. Rotate so the extrusion thickness points along +Y,
        # and translate so the solid's bounding box minimum corner is at the origin.
        oriented = solid.rotate((0, 0, 0), (1, 0, 0), 90)
    
        bb = oriented.val().BoundingBox()
        oriented = oriented.translate((-bb.xmin, -bb.ymin, -bb.zmin))
    
        return oriented
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00039777/gpt_generated.stl')
