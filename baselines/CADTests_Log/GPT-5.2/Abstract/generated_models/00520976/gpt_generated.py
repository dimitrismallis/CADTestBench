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
        base_size = 50.0
        height = 20.0
        small_size = base_size / 5.0
        cut_depth = height  # cut through the full height
    
        # Base solid: square extruded along +Z, centered in XY
        result = cq.Workplane("XY").rect(base_size, base_size).extrude(height)
    
        # Cut a smaller square from the top-right corner
        # Base top-right corner in XY is at (base_size/2, base_size/2)
        # For the small square to have its top-right corner touch that point,
        # its center must be shifted left/down by small_size/2.
        cx = base_size / 2.0 - small_size / 2.0
        cy = base_size / 2.0 - small_size / 2.0
    
        result = (
            result
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(cx, cy)
            .rect(small_size, small_size)
            .cutBlind(-cut_depth)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00520976/gpt_generated.stl')
