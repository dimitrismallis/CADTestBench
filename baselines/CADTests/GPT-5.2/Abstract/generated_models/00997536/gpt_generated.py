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
        # Parameters (mm)
        cyl_radius = 20.0
        cyl_height = 30.0
    
        # Regular octagon size (across flats)
        oct_across_flats = 18.0
        # CadQuery polygon() uses circumscribed circle diameter, so convert:
        # across_flats = 2 * R * cos(pi/n)  =>  R = across_flats / (2*cos(pi/n))
        n = 8
        R = oct_across_flats / (2.0 * math.cos(math.pi / n))
        oct_circ_diam = 2.0 * R
    
        result = (
            cq.Workplane("XY")
            .circle(cyl_radius)
            .extrude(cyl_height)
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .polygon(n, oct_circ_diam)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00997536/gpt_generated.stl')
