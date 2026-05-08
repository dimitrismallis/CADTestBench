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
        # --- Given parameters (units as provided) ---
        total_base_len = 0.676776
        base_y = 0.20312  # "width of the base" interpreted as baseline Y offset
    
        # Heights above the baseline at key points
        h_peak1 = 0.102138
        h_trough12 = 0.059507
        h_peak2 = 0.135891
        h_trough23 = 0.05773
        h_peak3 = 0.089704
    
        extrude_len = 0.75
        x_translate = -0.349931
    
        # --- Choose x-positions along the base ---
        # We have 6 key x positions: left end, peak1, trough12, peak2, trough23, peak3, right end.
        # Only total base length is specified, so we distribute the key points evenly along X.
        x0 = 0.0
        x6 = total_base_len
        step = total_base_len / 6.0
        x1 = x0 + step
        x2 = x0 + 2 * step
        x3 = x0 + 3 * step
        x4 = x0 + 4 * step
        x5 = x0 + 5 * step
    
        # --- Build the 2D profile (front view) in XY ---
        # Baseline is at y=base_y; peaks/troughs are at base_y + given height.
        pts = [
            (x0, base_y),                 # left base
            (x1, base_y + h_peak1),        # peak 1
            (x2, base_y + h_trough12),     # trough between 1 and 2
            (x3, base_y + h_peak2),        # peak 2 (center)
            (x4, base_y + h_trough23),     # trough between 2 and 3
            (x5, base_y + h_peak3),        # peak 3
            (x6, base_y),                 # right base
            (x6, 0.0),                    # down to bottom to close a solid region
            (x0, 0.0),                    # back to left bottom
        ]
    
        profile = (
            cq.Workplane("XY")
            .moveTo(*pts[0])
            .lineTo(*pts[1])
            .lineTo(*pts[2])
            .lineTo(*pts[3])
            .lineTo(*pts[4])
            .lineTo(*pts[5])
            .lineTo(*pts[6])
            .lineTo(*pts[7])
            .lineTo(*pts[8])
            .close()
        )
    
        solid = profile.extrude(extrude_len)
    
        # --- Translate along X as requested ---
        solid = solid.translate((x_translate, 0, 0))
    
        return solid
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00671898/gpt_generated.stl')
