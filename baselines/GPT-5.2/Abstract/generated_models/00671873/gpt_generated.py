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
        base_len = 80.0       # overall length in X of the base step
        base_h   = 20.0       # height in Y of the base step
        top_len  = 45.0       # length in X of the upper step (centered)
        top_h    = 15.0       # height in Y of the upper step
        depth_z  = 50.0       # extrusion depth in Z
    
        # Derived half-dimensions
        bx = base_len / 2.0
        tx = top_len / 2.0
        total_h = base_h + top_h
    
        # Build a single connected side profile (L-shaped) as one closed wire
        # Coordinates in XY:
        # (-bx,0) -> (bx,0) -> (bx,base_h) -> (tx,base_h) -> (tx,total_h)
        # -> (-tx,total_h) -> (-tx,base_h) -> (-bx,base_h) -> close
        profile = (
            cq.Workplane("XY")
            .moveTo(-bx, 0)
            .lineTo(bx, 0)
            .lineTo(bx, base_h)
            .lineTo(tx, base_h)
            .lineTo(tx, total_h)
            .lineTo(-tx, total_h)
            .lineTo(-tx, base_h)
            .lineTo(-bx, base_h)
            .close()
        )
    
        result = profile.extrude(depth_z)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00671873/gpt_generated.stl')
