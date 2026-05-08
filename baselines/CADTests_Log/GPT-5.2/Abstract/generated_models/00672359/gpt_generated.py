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
        side = 30.0          # square side length (also triangle leg lengths)
        thickness = 4.0      # small extrusion amount
    
        # Build the combined 2D profile on XY:
        # Square centered at origin: corners at (+/-side/2, +/-side/2)
        # Triangle attached to the top edge of the square:
        #   - one right-angle leg coincident with the square's top edge (length = side)
        #   - the other right-angle leg goes upward from the top-left corner (length = side)
        # This yields an "irregular rhombus-like" outline (a square with a triangular cap).
        profile = (
            cq.Workplane("XY")
            # square
            .rect(side, side)
            # triangle sharing the top edge of the square
            .moveTo(-side/2, side/2)          # top-left corner of square
            .lineTo(side/2, side/2)           # along top edge (leg 1)
            .lineTo(-side/2, side/2 + side)   # up from top-left (leg 2)
            .close()
            # make a single face from the two closed wires
            .combine()
        )
    
        # Extrude the entire sketch
        result = profile.extrude(thickness)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00672359/gpt_generated.stl')
