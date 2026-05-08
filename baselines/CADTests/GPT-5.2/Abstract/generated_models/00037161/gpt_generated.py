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
        square_size = 40.0
        thickness = 5.0
        hole_w = 8.0
        hole_h = 4.0
    
        result = (
            cq.Workplane("XY")
            .rect(square_size, square_size)
            .extrude(thickness)
            .faces(">Z")
            .workplane()
            .rect(hole_w, hole_h)
            .cutThruAll()
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00037161/gpt_generated.stl')
