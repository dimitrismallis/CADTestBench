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
        w = 60.0          # base rectangle width (X)
        h = 40.0          # base rectangle height (Y)
        cut = 12.0        # cut distance along top edge from each corner
        t = 3.0           # extrusion thickness (Z)
    
        # Ensure cut is valid
        cut = max(0.0, min(cut, w / 2.0 - 0.1))
    
        # Rectangle corners (centered at origin), with top corners cut off:
        # Start at bottom-left and go CCW
        pts = [
            (-w/2, -h/2),          # bottom-left
            ( w/2, -h/2),          # bottom-right
            ( w/2,  h/2 - cut),    # right side up to start of cut
            ( w/2 - cut,  h/2),    # top-right cut point
            (-w/2 + cut,  h/2),    # top-left cut point
            (-w/2,  h/2 - cut),    # left side down to start of cut
        ]
    
        tile = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(t)
        )
    
        return tile
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00681547/gpt_generated.stl')
