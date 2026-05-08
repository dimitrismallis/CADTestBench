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
        # Units as given in prompt (CadQuery default is mm, but we treat these as "units")
        side = 1.5
        thickness = 0.09375
    
        tri_leg_bottom = 1.125   # along bottom edge, from bottom-right corner going left
        tri_leg_right  = 1.3125  # along right edge, from bottom-right corner going up
    
        # Base square plate, centered on origin
        plate = cq.Workplane("XY").box(side, side, thickness, centered=(True, True, False))
    
        # Cut triangle: right angle at bottom-right corner of the square
        # bottom-right corner in XY is (x=+side/2, y=-side/2)
        result = (
            plate
            .faces(">Z")
            .vertices(">X and <Y")     # select bottom-right vertex of the top face
            .workplane(centerOption="CenterOfMass")
            .moveTo(0, 0)              # at the corner
            .lineTo(-tri_leg_bottom, 0)  # left along bottom edge
            .lineTo(0, tri_leg_right)    # up along right edge
            .close()
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00673788/gpt_generated.stl')
