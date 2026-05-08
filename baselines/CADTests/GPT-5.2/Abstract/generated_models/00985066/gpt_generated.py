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
        outer_w = 80.0          # overall width (X)
        outer_h = 60.0          # overall height (Y) of the 2D profile
        depth   = 30.0          # extrusion depth (Z)
    
        col_w   = 14.0          # width of each upright column (slightly larger)
        beam_h  = 10.0          # thickness of the horizontal section (bottom beam)
    
        # Derived inner cutout size:
        inner_w = outer_w - 2.0 * col_w
        inner_h = outer_h - beam_h
    
        # Shift the inner cutout upward so the remaining material at the bottom is beam_h
        inner_center_y = beam_h / 2.0
    
        # --- Build 2D U-shape and extrude ---
        u_solid = (
            cq.Workplane("XY")
            .rect(outer_w, outer_h)                         # outer boundary
            .rect(inner_w, inner_h)                         # inner cutout (to be subtracted)
            .translate((0, inner_center_y, 0))              # move inner cutout up
            .extrude(depth)                                 # extrude into 3D
        )
    
        return u_solid
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00985066/gpt_generated.stl')
