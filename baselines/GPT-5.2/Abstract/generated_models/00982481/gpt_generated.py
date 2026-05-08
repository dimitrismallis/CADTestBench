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
        # Parameters
        cyl_radius = 10.0
        cyl_height = 30.0
    
        big_radius = 16.0          # larger than cylinder radius
        big_extrude = 6.0          # height of the upper feature
        offset_xy = (4.0, 0.0)     # place it near the top (slightly off-center)
    
        # Base cylinder
        result = cq.Workplane("XY").circle(cyl_radius).extrude(cyl_height)
    
        # Larger circle near the top of the cylinder, then extrude
        result = (
            result
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(offset_xy[0], offset_xy[1])
            .circle(big_radius)
            .extrude(big_extrude)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00982481/gpt_generated.stl')
