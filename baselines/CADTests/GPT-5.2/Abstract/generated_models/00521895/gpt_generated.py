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
        base_len = 80.0
        base_wid = 50.0
        base_thk = 8.0
    
        tube_outer_d = 24.0
        tube_inner_d = 14.0
        tube_h = 20.0
    
        # Base rectangle extruded
        part = (
            cq.Workplane("XY")
            .rect(base_len, base_wid)
            .extrude(base_thk)
        )
    
        # Hollow cylinder (tube) in the middle of the rectangle, on top face
        part = (
            part
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .circle(tube_outer_d / 2.0)
            .circle(tube_inner_d / 2.0)
            .extrude(tube_h)
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00521895/gpt_generated.stl')
