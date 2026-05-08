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
        plate_w = 80.0   # X size
        plate_h = 50.0   # Y size
        plate_t = 4.0    # thickness (slight extrude)
    
        hole_w = plate_w * 0.5   # 1/4 area => 1/2 width and 1/2 height
        hole_h = plate_h * 0.5
    
        bottom_margin = 5.0  # small space between hole bottom and plate bottom
    
        # Compute hole center Y so that hole's bottom edge is bottom_margin above plate bottom edge
        # Plate spans Y: [-plate_h/2, +plate_h/2]
        # Hole spans  Y: [yc - hole_h/2, yc + hole_h/2]
        # Want: yc - hole_h/2 = -plate_h/2 + bottom_margin
        hole_center_y = (-plate_h / 2.0 + bottom_margin) + hole_h / 2.0
    
        result = (
            cq.Workplane("XY")
            .rect(plate_w, plate_h)
            .extrude(plate_t)
            .faces(">Z").workplane()
            .center(0, hole_center_y)
            .rect(hole_w, hole_h)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00684686/gpt_generated.stl')
