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
        square_size = 100.0   # side length of the square
        thickness = 5.0       # slight extrusion
        tri_leg_x = 45.0      # triangle leg along -X from bottom-right corner
        tri_leg_y = 35.0      # triangle leg along +Y from bottom-right corner
    
        half = square_size / 2.0
    
        # Base: square plate, centered on origin
        plate = cq.Workplane("XY").box(square_size, square_size, thickness, centered=(True, True, False))
    
        # Cut: right triangle from bottom-right corner (x=+half, y=-half)
        # Right angle at the corner, legs extend left (-X) and up (+Y)
        cut_tri = (
            plate
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .moveTo(half, -half)
            .lineTo(half - tri_leg_x, -half)
            .lineTo(half, -half + tri_leg_y)
            .close()
            .cutThruAll()
        )
    
        return cut_tri
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00673788/gpt_generated.stl')
