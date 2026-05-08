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
        square_size = 20.0   # mm (side length)
        extrude_h   = 150.0  # mm (extensive extrusion)
    
        # Model: square (as a rectangle) then extrude
        result = (
            cq.Workplane("XY")
            .rect(square_size, square_size)
            .extrude(extrude_h)
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00008835/gpt_generated.stl')
