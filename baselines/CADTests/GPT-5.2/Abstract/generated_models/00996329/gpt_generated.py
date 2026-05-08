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
        leg_x = 40.0          # overall length in X
        leg_y = 30.0          # overall length in Y
        arm = 8.0             # width of the L arms in the 2D profile
        height = 6.0          # extrusion height in Z
    
        # L profile: outer rectangle minus inner rectangle shifted to top-right
        sk = (
            cq.Sketch()
            .rect(leg_x, leg_y)  # outer
            .push([(arm / 2.0, arm / 2.0)])  # shift inner cutout to top-right
            .rect(leg_x - arm, leg_y - arm, mode="s")  # subtract inner
        )
    
        bracket = cq.Workplane("XY").placeSketch(sk).extrude(height)
        return bracket
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00996329/gpt_generated.stl')
