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
        L = 0.47368   # length (X)
        W = 0.31579   # width  (Y)  -> "shorter edge" direction
        H = 0.75      # height (Z)
    
        hole_d = 0.196206
        hole_r = hole_d / 2.0
    
        top_offset = 0.146132  # top of (reference) cylinder below top surface
    
        slit_w = 0.007895
        slit_depth = 0.196132  # cut depth from top surface downward
    
        # --- Base block ---
        block = cq.Workplane("XY").box(L, W, H, centered=True)
    
        # --- Through hole ---
        # Create a workplane parallel to top face, offset downward by top_offset.
        # Then cut a circular hole through the entire block.
        block = (
            block
            .faces(">Z").workplane(offset=-top_offset, centerOption="CenterOfMass")
            .circle(hole_r)
            .cutThruAll()
        )
    
        # --- Slit ("wire-cutter" style) ---
        # Slit runs from hole center toward the nearest short edge (along +Y),
        # starting at the hole edge and extending to the outer edge.
        # Cut from the top face down by slit_depth.
        y_start = hole_r
        y_end = W / 2.0
        slit_len = max(0.0, y_end - y_start)
        slit_center_y = (y_start + y_end) / 2.0
    
        # If geometry is degenerate (shouldn't be), avoid zero-length cut
        if slit_len <= 1e-9:
            return block
    
        block = (
            block
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(0, slit_center_y)
            .rect(slit_w, slit_len)
            .cutBlind(-slit_depth)
        )
    
        return block
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00034100/gpt_generated.stl')
