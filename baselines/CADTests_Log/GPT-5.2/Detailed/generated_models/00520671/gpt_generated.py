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
        base_d = 1.5
        base_h = 0.06
    
        boss_d = 0.75
        boss_h = 0.375
    
        cut_len = 0.21   # along X
        cut_wid = 0.45   # along Y
        pad = 0.12       # inset from outer edge of base (radially, on +X side)
    
        base_r = base_d / 2.0
    
        # Compute rectangle center position so that its right edge is (base_r - pad)
        # right_edge_x = x_center + cut_len/2 = base_r - pad
        cut_center_x = (base_r - pad) - (cut_len / 2.0)
    
        # --- Model ---
        base = cq.Workplane("XY").circle(base_r).extrude(base_h)
    
        boss = (
            cq.Workplane("XY")
            .workplane(offset=base_h)  # start boss on top of base
            .circle(boss_d / 2.0)
            .extrude(boss_h)
        )
    
        part = base.union(boss)
    
        # Cut rectangle from the first cylinder (base) only: cut depth = base_h from top face
        part = (
            part
            .faces(">Z")                 # topmost face (boss top)
            .workplane()                 # workplane at boss top
            .workplane(offset=-boss_h)   # move down to base top surface
            .center(cut_center_x, 0)
            .rect(cut_len, cut_wid)
            .cutBlind(-base_h)           # cut down through base thickness only
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00520671/gpt_generated.stl')
