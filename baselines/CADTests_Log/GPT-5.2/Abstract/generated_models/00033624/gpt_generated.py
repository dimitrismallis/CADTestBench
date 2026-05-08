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
        length = 120.0
        width = 25.0
        thickness = 6.0
    
        hole_d = 6.0
        end_offset = 12.0          # distance from the end face to hole centers
        hole_spacing_y = 12.0      # distance between the two holes (Y direction)
    
        # --- Base plate ---
        plate = cq.Workplane("XY").rect(length, width).extrude(thickness)
    
        # --- Holes near one end (choose +X end) ---
        x_hole = (length / 2.0) - end_offset
        y1 = -hole_spacing_y / 2.0
        y2 =  hole_spacing_y / 2.0
    
        result = (
            plate
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints([(x_hole, y1), (x_hole, y2)])
            .hole(hole_d)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00033624/gpt_generated.stl')
