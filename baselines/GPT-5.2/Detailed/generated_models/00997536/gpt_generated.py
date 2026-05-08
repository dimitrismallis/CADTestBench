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
        cyl_d = 0.988192
        cyl_h = 0.75
    
        oct_d = 0.79436          # interpreted as diameter of circumscribed circle (across vertices)
        oct_sides = 8
    
        # Outer cylinder
        result = (
            cq.Workplane("XY")
            .circle(cyl_d / 2.0)
            .extrude(cyl_h)
        )
    
        # Octagonal through-hole (centered)
        result = (
            result
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .polygon(oct_sides, oct_d)   # polygon(diameter= circumscribed circle diameter)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00997536/gpt_generated.stl')
