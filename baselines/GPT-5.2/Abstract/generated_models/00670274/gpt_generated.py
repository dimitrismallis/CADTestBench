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
        length = 80.0
        width = 50.0
        thickness = 6.0
    
        cutout_size = 8.0  # square cutout side length
    
        # Base solid from a rectangle sketch
        part = cq.Workplane("XY").rect(length, width).extrude(thickness)
    
        # Corner cutouts: place 4 squares on the top face and cut through all
        x_off = length / 2 - cutout_size / 2
        y_off = width / 2 - cutout_size / 2
        corner_pts = [
            ( x_off,  y_off),
            (-x_off,  y_off),
            (-x_off, -y_off),
            ( x_off, -y_off),
        ]
    
        part = (
            part.faces(">Z")
            .workplane()
            .pushPoints(corner_pts)
            .rect(cutout_size, cutout_size)
            .cutThruAll()
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00670274/gpt_generated.stl')
