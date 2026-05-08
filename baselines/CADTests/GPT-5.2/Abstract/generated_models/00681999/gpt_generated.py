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
        W = 90.0                 # rectangle width
        H = (2.0 / 3.0) * W      # rectangle height (~2/3 of width)
        s = (1.0 / 3.0) * W      # square cutout side (~1/3 of rectangle size)
        thickness = 12.0         # extrusion height
    
        # Base rectangle centered at origin => top edge at y=+H/2
        # Square cutout centered in X, with its top edge coincident with rectangle top edge
        square_center_y = (H / 2.0) - (s / 2.0)
    
        base = cq.Workplane("XY").rect(W, H).extrude(thickness)
    
        result = (
            base.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .center(0, square_center_y)
            .rect(s, s)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00681999/gpt_generated.stl')
