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
        n_points = 5
        r_outer = 30.0
        r_inner = 13.0
        thickness = 8.0
    
        # Each outer vertex gets a different angular perturbation (degrees)
        outer_angle_jitter_deg = [0.0, 3.0, -2.0, 4.5, -3.5]
        # Smaller perturbation for inner vertices
        inner_angle_jitter_deg = [0.0, -1.0, 1.5, -0.5, 0.5]
    
        # --- Build star points (outer/inner alternating) ---
        pts = []
        base_step = 360.0 / n_points  # 72 degrees
    
        for i in range(n_points):
            ang_outer = i * base_step + outer_angle_jitter_deg[i]
            ao = math.radians(ang_outer)
            pts.append((r_outer * math.cos(ao), r_outer * math.sin(ao)))
    
            ang_inner = i * base_step + base_step / 2.0 + inner_angle_jitter_deg[i]
            ai = math.radians(ang_inner)
            pts.append((r_inner * math.cos(ai), r_inner * math.sin(ai)))
    
        # --- Create 2D wire, make face, extrude ---
        star = (
            cq.Workplane("XY")
            .moveTo(*pts[0])
            .polyline(pts[1:])
            .close()
            .wire()          # ensure we have a wire on the stack
            .toPending()     # treat it as pending wire for extrusion
            .extrude(thickness)
        )
    
        return star
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00681589/gpt_generated.stl')
