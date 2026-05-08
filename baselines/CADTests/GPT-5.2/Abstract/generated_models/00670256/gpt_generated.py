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
        outer_len = 60.0   # X
        outer_wid = 30.0   # Y
        height    = 20.0   # Z (short pipe)
        wall      = 3.0    # wall thickness
    
        inner_len = outer_len - 2 * wall
        inner_wid = outer_wid - 2 * wall
        if inner_len <= 0 or inner_wid <= 0:
            raise ValueError("Wall thickness too large for given outer dimensions.")
    
        # --- Model ---
        tube = (
            cq.Workplane("XY")
            .rect(outer_len, outer_wid)
            .extrude(height)
            .faces(">Z")
            .workplane()
            .rect(inner_len, inner_wid)
            .cutThruAll()
        )
    
        return tube
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00670256/gpt_generated.stl')
