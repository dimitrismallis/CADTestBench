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
        top_len = 160.0          # overall length of the surface (X)
        top_wid = 80.0           # overall width of the surface (Y)
        corner_cut = 12.0        # corner chamfer amount (equivalent to cutting right triangles)
        top_thk = 6.0            # thickness of the surface
    
        leg_flat_diam = 50.0     # polygon() diameter (across vertices)
        leg_height = 90.0        # height of hex columns
        leg_x_offset = 55.0      # symmetric X offset of leg centers
    
        L2, W2, c = top_len / 2.0, top_wid / 2.0, corner_cut
    
        # Octagon points (rectangle with 45° corner cuts)
        pts = [
            (-L2 + c, -W2),
            ( L2 - c, -W2),
            ( L2,     -W2 + c),
            ( L2,      W2 - c),
            ( L2 - c,  W2),
            (-L2 + c,  W2),
            (-L2,      W2 - c),
            (-L2,     -W2 + c),
        ]
    
        top = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(top_thk)
        )
    
        # Two hexagonal columns protruding from the top face
        result = (
            top
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints([(-leg_x_offset, 0.0), (leg_x_offset, 0.0)])
            .polygon(6, leg_flat_diam)
            .extrude(leg_height)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00998698/gpt_generated.stl')
