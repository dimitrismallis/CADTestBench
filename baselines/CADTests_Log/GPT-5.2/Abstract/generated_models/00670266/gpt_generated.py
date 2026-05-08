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
        w = 50.0          # overall width (X)
        h = 30.0          # overall height (Y)
        t = 3.0           # thickness (Z)
        corner_r = 6.0    # radius for the two top corners
        hole_d = 6.0      # circular cutout diameter
        hole_drop = 6.0   # distance down from the top edge to hole center
    
        # 2D profile: rectangle with only the top corners rounded
        # Rectangle corners (centered at origin):
        # bottom-left  (-w/2, -h/2)
        # bottom-right ( w/2, -h/2)
        # top-right    ( w/2,  h/2)
        # top-left     (-w/2,  h/2)
        xL, xR = -w / 2, w / 2
        yB, yT = -h / 2, h / 2
        r = min(corner_r, w / 2 - 0.1, h / 2 - 0.1)
    
        profile = (
            cq.Workplane("XY")
            .moveTo(xL, yB)
            .lineTo(xR, yB)
            .lineTo(xR, yT - r)
            .radiusArc((xR - r, yT), r)      # top-right rounded corner
            .lineTo(xL + r, yT)
            .radiusArc((xL, yT - r), r)      # top-left rounded corner
            .lineTo(xL, yB)
            .close()
        )
    
        tag = profile.extrude(t)
    
        # Circular cutout: centered in X, slightly below top edge, through all
        hole_y = yT - hole_drop
        tag = (
            tag.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .center(0, hole_y)   # workplane is on top face; its 2D coords match XY
            .hole(hole_d)
        )
    
        return tag
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00670266/gpt_generated.stl')
