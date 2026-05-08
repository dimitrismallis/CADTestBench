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
        bottom_len = 0.495408
        top_len    = 0.148743
        trap_h     = 0.233091
        prism_w    = 0.744939  # total extrusion thickness along Z
    
        # Center the trapezoid about the origin in XY:
        # Height along Y, centered at Y=0
        y_bot = -trap_h / 2.0
        y_top =  trap_h / 2.0
    
        xb = bottom_len / 2.0
        xt = top_len / 2.0
    
        pts = [
            (-xb, y_bot),
            ( xb, y_bot),
            ( xt, y_top),
            (-xt, y_top),
        ]
    
        half_w = prism_w / 2.0
    
        # Build profile then extrude symmetrically about Z=0
        result = (
            cq.Workplane("XY")
            .polyline(pts).close()
            .extrude(half_w)                 # extrude +Z
            .faces("<Z").workplane()         # go to bottom face
            .polyline(pts).close()           # re-create same profile on that face
            .extrude(half_w)                 # extrude further in -Z direction (from bottom face)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00985494/gpt_generated.stl')
