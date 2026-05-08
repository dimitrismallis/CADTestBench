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
        length = 200.0   # large rectangle length (X)
        width  = 120.0   # large rectangle width (Y)
        thickness = 2.0  # marginal extrusion (Z)
    
        result = (
            cq.Workplane("XY")
            .rect(length, width)
            .extrude(thickness)
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00006013/gpt_generated.stl')
