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
        base_len = 80.0   # X size
        base_wid = 50.0   # Y size
        base_h   = 12.0   # Z height
    
        # L-shape dimensions (built from two rectangles sharing the same corner)
        leg_x = 30.0      # length along X from the corner
        leg_y = 25.0      # length along Y from the corner
        thick = 10.0      # thickness of each leg
        l_h   = 18.0      # height of L block
    
        # --- Base block: sketch rectangle then extrude ---
        base = (
            cq.Workplane("XY")
            .rect(base_len, base_wid)
            .extrude(base_h)
        )
    
        # --- L block on top, aligned to one corner of the base (top-right corner) ---
        # Move workplane origin to the top-right corner of the top face:
        # top-right corner in XY is (+base_len/2, +base_wid/2)
        result = (
            base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(base_len / 2.0, base_wid / 2.0)
            # Create L-shape as union of two rectangles, both anchored at the corner.
            # Use centered=False so each rectangle starts at the corner and extends +X/+Y.
            .rect(leg_x, thick, centered=False)
            .rect(thick, leg_y, centered=False)
            .extrude(l_h)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00998012/gpt_generated.stl')
