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
        # Parameters (units as given)
        base_w = 0.440093   # X size
        base_h = 0.143395   # Y size
        base_depth = 0.143395  # Z thickness of base
    
        # Wall ring dimensions (as provided; note prompt mixes "width/length")
        inner_w = 0.382387  # X inner opening
        inner_l = 0.721321  # Y inner opening (larger than outer; will be clamped)
    
        wall_height = 0.131228
        inside_corner_r = 0.017381
    
        # If inner dimensions exceed outer, clamp to a safe value so the model is valid
        safe_inner_x = min(inner_w, base_w - 1e-6)
        safe_inner_y = min(inner_l, base_h - 1e-6)
    
        # Base
        part = cq.Workplane("XY").rect(base_w, base_h).extrude(base_depth)
    
        # Walls: rectangular ring on top face
        part = (
            part
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(base_w, base_h)
            .rect(safe_inner_x, safe_inner_y)
            .extrude(wall_height)
        )
    
        # Round/chamfer inside corners: fillet the inner vertical edges
        # Select vertical edges that belong to the inner opening by using a bounding box filter.
        # Inner opening edges lie near +/- safe_inner_x/2 and +/- safe_inner_y/2.
        tol = 1e-6
        x0, x1 = -safe_inner_x/2 - tol, safe_inner_x/2 + tol
        y0, y1 = -safe_inner_y/2 - tol, safe_inner_y/2 + tol
        z0, z1 = base_depth - tol, base_depth + wall_height + tol
    
        inner_vertical_edges = (
            part
            .edges("|Z")
            .filter(lambda e: (
                (x0 <= e.Center().x <= x1) and
                (y0 <= e.Center().y <= y1) and
                (z0 <= e.Center().z <= z1)
            ))
        )
    
        # Apply fillet (rounded inside corners)
        part = inner_vertical_edges.fillet(inside_corner_r)
    
        # Translate to requested center position:
        # (length/2 - 0.030417, width/2 - 0.030417 + 0.001564, height/2)
        # Interpret "length" as Y (base_h), "width" as X (base_w), "height" as total Z.
        total_height = base_depth + wall_height
        tx = base_h / 2.0 - 0.030417
        ty = base_w / 2.0 - 0.030417 + 0.001564
        tz = total_height / 2.0
    
        part = part.translate((tx, ty, tz))
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00998749/gpt_generated.stl')
