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
        L = 0.00875   # length (X)
        W = 0.74801   # width  (Y)
        H = 0.03125   # height (Z)
    
        cut_w = 0.1625   # cutout width in X
        cut_h = 0.0125   # cutout height in Y
        cut_from_left = 0.01875  # distance from left edge (X-min) to cutout's left edge
    
        # Place cutout near the bottom edge (Y-min). Not specified, so choose a small margin.
        bottom_margin = 0.002  # keeps the cutout inside the part
    
        # --- Base solid ---
        base = cq.Workplane("XY").box(L, W, H, centered=True)
    
        # Compute cutout center position in the top-face workplane coordinates
        x_min = -L / 2.0
        y_min = -W / 2.0
    
        cut_center_x = x_min + cut_from_left + cut_w / 2.0
        cut_center_y = y_min + bottom_margin + cut_h / 2.0
    
        # --- Cutout (pocket) ---
        result = (
            base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(cut_center_x, cut_center_y)
            .rect(cut_w, cut_h)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00997068/gpt_generated.stl')
