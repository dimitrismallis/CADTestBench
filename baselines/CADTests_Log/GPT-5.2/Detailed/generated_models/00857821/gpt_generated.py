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
        diameter = 0.374906
        height = 0.1875
    
        # Circle definition
        r = diameter / 2.0
        circle_center = (diameter / 2.0, diameter * 2.0 - 0.187124)
    
        # Polygon definition (3 points)
        poly_pts = [
            (0.0, 0.0),
            (0.0, diameter),
            ((diameter * 0.7) + 0.01883 - 0.0001, diameter),
        ]
    
        # Build 2D profile: circle + polygon, then extrude
        profile = (
            cq.Workplane("XY")
            .center(circle_center[0], circle_center[1])
            .circle(r)
            .center(-circle_center[0], -circle_center[1])  # return to global origin
            .polyline(poly_pts).close()
            .combine()  # union the pending wires into a single face if possible
        )
    
        solid = profile.extrude(height)
    
        # Center vertically about XY plane
        solid = solid.translate((0, 0, -height / 2.0))
    
        return solid
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00857821/gpt_generated.stl')
