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
        rect_len = 0.345
        rect_wid = 0.0024
        base_thk = 0.0024  # "marginally extruded" thickness (small)
    
        rod_x = 0.00375
        rod_y = 0.75
        rod_h = 3.0 * rect_len  # height is 3x rectangle length
        # (Given 0.0075 as third dimension conflicts with the height rule; we follow the rule.)
    
        # --- Base plate ---
        base = cq.Workplane("XY").rect(rect_len, rect_wid).extrude(base_thk)
    
        # --- Rod at one corner, pointing up (+Z) ---
        # Place rod so its bottom sits on the top face, and its footprint is at the +X,+Y corner.
        rod = (
            base.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .center(rect_len / 2 - rod_x / 2, rect_wid / 2 - rod_y / 2)
            .rect(rod_x, rod_y)
            .extrude(rod_h, combine=True)
        )
    
        return rod
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00019066/gpt_generated.stl')
