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
        # Baseline runs along +X, profile is in the XY plane, extrude in +Z.
        b_left = 30.0
        b_center = 40.0
        b_right = 28.0
    
        # Heights of the peaks (Y direction)
        h_left = 22.0
        h_center = (math.sqrt(3) / 2.0) * b_center  # equilateral triangle height
        h_right = 18.0
    
        # Peak X positions (chosen to make side triangles scalene and acute)
        # Must be strictly inside each base interval to keep triangles acute-ish.
        x0 = 0.0
        x1 = x0 + b_left
        x2 = x1 + b_center
        x3 = x2 + b_right
    
        x_peak_left = x0 + 0.42 * b_left
        x_peak_center = x1 + 0.50 * b_center
        x_peak_right = x2 + 0.62 * b_right
    
        # Extrusion thickness
        thickness = 20.0
    
        # --- Construct outline points (single closed polygon) ---
        # Start at left baseline, go up/down across the three peaks, end at right baseline, then close along baseline.
        pts = [
            (x0, 0.0),                 # leftmost base
            (x_peak_left, h_left),     # left peak
            (x1, 0.0),                 # left/center junction on base
            (x_peak_center, h_center), # center peak (equilateral)
            (x2, 0.0),                 # center/right junction on base
            (x_peak_right, h_right),   # right peak
            (x3, 0.0),                 # rightmost base
        ]
    
        # Center the profile about X=0 for nicer placement
        x_mid = (x0 + x3) / 2.0
        pts_centered = [(x - x_mid, y) for (x, y) in pts]
    
        # --- Build and extrude ---
        profile = (
            cq.Workplane("XY")
            .polyline(pts_centered)
            .close()
        )
    
        result = profile.extrude(thickness)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00671898/gpt_generated.stl')
