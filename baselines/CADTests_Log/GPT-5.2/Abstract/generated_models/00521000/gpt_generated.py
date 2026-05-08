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
        outer_d = 30.0
        ring_radial_width = 2.0          # small ring width (radial thickness)
        height = 3.0                     # ring height (axial thickness)
    
        inner_d = outer_d - 2.0 * ring_radial_width
    
        hole_d = 1.2                     # smaller than ring_radial_width (2.0)
        hole_r = hole_d / 2.0
    
        # Place holes on a bolt circle that stays within the ring material
        outer_r = outer_d / 2.0
        inner_r = inner_d / 2.0
        bolt_r = (outer_r + inner_r) / 2.0  # mid-thickness radius
    
        # --- Model ---
        ring = (
            cq.Workplane("XY")
            .circle(outer_r)
            .circle(inner_r)
            .extrude(height)
        )
    
        # Equilateral triangle points (120° apart)
        pts = [
            (bolt_r * math.cos(a), bolt_r * math.sin(a))
            for a in [0, 2 * math.pi / 3, 4 * math.pi / 3]
        ]
    
        result = (
            ring
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints(pts)
            .circle(hole_r)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00521000/gpt_generated.stl')
