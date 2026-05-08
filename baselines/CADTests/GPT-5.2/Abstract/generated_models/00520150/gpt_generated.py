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
        outer_w = 60.0   # overall width in X
        outer_h = 60.0   # overall height in Y
        leg_t   = 15.0   # thickness of the L legs
        extrude_h = 20.0 # extrusion height in Z
    
        # L shape = outer rectangle minus inner cutout rectangle
        # Inner cutout size leaves two legs of thickness leg_t
        cut_w = outer_w - leg_t
        cut_h = outer_h - leg_t
    
        result = (
            cq.Workplane("XY")
            .rect(outer_w, outer_h)
            .extrude(extrude_h)
            .faces(">Z").workplane()
            .center(leg_t/2, leg_t/2)          # shift cutout to top-right corner region
            .rect(cut_w, cut_h)
            .cutBlind(-extrude_h)              # cut down through the full height
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00520150/gpt_generated.stl')
