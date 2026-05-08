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
        outer_r = 40.0          # outer radius of sector
        wall = 3.0              # radial wall thickness
        inner_r = outer_r - wall
        angle_deg = 50.0        # minor sector angle
        height = 20.0           # extrusion height
    
        def sector_profile(wp: cq.Workplane, r: float, ang_deg: float) -> cq.Workplane:
            """Create a closed circular sector wire as pending geometry on wp."""
            a = math.radians(ang_deg)
            p1 = (r, 0.0)
            p2 = (r * math.cos(a), r * math.sin(a))
            return (
                wp.moveTo(*p1)
                  .radiusArc(p2, r)   # arc of radius r (center implied by geometry)
                  .lineTo(0.0, 0.0)
                  .close()
            )
    
        # Outer solid sector
        outer = sector_profile(cq.Workplane("XY"), outer_r, angle_deg).extrude(height)
    
        # Inner cut: sketch on top face, then cut through all
        result = (
            outer
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .moveTo(inner_r, 0.0)
            .radiusArc(
                (inner_r * math.cos(math.radians(angle_deg)),
                 inner_r * math.sin(math.radians(angle_deg))),
                inner_r
            )
            .lineTo(0.0, 0.0)
            .close()
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00684841/gpt_generated.stl')
