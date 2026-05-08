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
        width = 30.0
        length = 5.0 * width
        base_thickness = 10.0
    
        cyl_radius = width / 3.0
        cyl_height = 20.0
    
        # Place cylinder near the +Y edge on the top face, with a small margin
        edge_margin = 1.0
        cyl_center_y = (width / 2.0) - cyl_radius - edge_margin
        cyl_center_x = 0.0  # centered along length
    
        base = cq.Workplane("XY").rect(length, width).extrude(base_thickness)
    
        result = (
            base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(cyl_center_x, cyl_center_y)
            .circle(cyl_radius)
            .extrude(cyl_height, combine=True)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00009998/gpt_generated.stl')
