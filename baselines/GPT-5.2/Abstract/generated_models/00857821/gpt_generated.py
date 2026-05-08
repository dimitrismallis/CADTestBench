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
        # --- Parameters ---
        size = 40.0          # overall scale of the heart in XY
        thickness = 10.0     # extrusion height in Z
        n_pts = 400          # curve sampling resolution (higher = smoother)
    
        # Classic parametric heart curve:
        # x = 16 sin^3(t)
        # y = 13 cos(t) - 5 cos(2t) - 2 cos(3t) - cos(4t)
        ts = np.linspace(0.0, 2.0 * math.pi, n_pts, endpoint=False)
        xs = 16.0 * (np.sin(ts) ** 3)
        ys = 13.0 * np.cos(ts) - 5.0 * np.cos(2.0 * ts) - 2.0 * np.cos(3.0 * ts) - np.cos(4.0 * ts)
    
        # Scale to requested size
        width = float(xs.max() - xs.min())
        height = float(ys.max() - ys.min())
        scale = size / max(width, height)
    
        pts = [(float(x * scale), float(y * scale)) for x, y in zip(xs, ys)]
    
        # Build a closed wire, make a face, and extrude
        heart = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .wire()
            .toPending()
            .extrude(thickness)
        )
    
        return heart
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00857821/gpt_generated.stl')
