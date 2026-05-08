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
        length = 80.0   # X direction (long side)
        width  = 30.0   # Y direction (short side)
        thick  = 6.0    # small extrusion thickness
    
        hole_d = 4.0
        edge_offset_x = 10.0   # distance from +X edge toward center
        end_margin_y  = 6.0    # keep holes away from +/-Y edges
    
        # Hole positions: aligned with the smaller side (Y), near one side (+X)
        x_hole = (length / 2.0) - edge_offset_x
        y_positions = [-width/2.0 + end_margin_y, 0.0, width/2.0 - end_margin_y]
    
        plate = (
            cq.Workplane("XY")
            .rect(length, width)
            .extrude(thick)
        )
    
        result = (
            plate
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints([(x_hole, y) for y in y_positions])
            .hole(hole_d)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00997373/gpt_generated.stl')
