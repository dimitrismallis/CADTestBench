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
        # Units assumed to be mm-equivalent "units" as given
        h = 0.375
        main_d = 1.5
        main_r = main_d / 2.0
    
        center_hole_d = 0.1875
    
        small_hole_d = 0.1125
        offset_r = 0.24375  # radial offset from center
    
        # Main body
        part = cq.Workplane("XY").cylinder(h, main_r)
    
        # Central through hole
        part = part.faces(">Z").workplane(centerOption="CenterOfMass").hole(center_hole_d)
    
        # Three holes on a triangular (120°) pattern
        pts = [
            (offset_r * math.cos(math.radians(a)), offset_r * math.sin(math.radians(a)))
            for a in (0, 120, 240)
        ]
    
        part = (
            part.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .pushPoints(pts)
            .hole(small_hole_d)
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00997300/gpt_generated.stl')
