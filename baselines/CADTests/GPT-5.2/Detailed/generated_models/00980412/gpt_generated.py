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
        # Parameters (units as given in prompt)
        base_len = 0.037173
        height_len = 0.759401
        thickness = 0.015931
    
        # Hollow wall thickness in 2D (chosen as a fraction of the smaller dimension)
        # Ensure it's not so large that the inner triangle collapses.
        wall = min(base_len, height_len) * 0.20  # 20% of the smaller side
    
        # Outer right triangle points (counter-clockwise)
        outer_pts = [(0, 0), (base_len, 0), (0, height_len)]
    
        # Inner right triangle points (offset inward by 'wall' along the legs)
        # Similar triangle with vertices at (wall, wall), (base_len-wall, wall), (wall, height_len-wall)
        inner_pts = [(wall, wall), (base_len - wall, wall), (wall, height_len - wall)]
    
        # Build hollow triangle as a planar face with a triangular hole, then extrude
        result = (
            cq.Workplane("XY")
            .polyline(outer_pts).close()
            .polyline(inner_pts).close()
            .extrude(thickness)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00980412/gpt_generated.stl')
