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
        width = 20.0
        length = 2.0 * width
        height = 10.0
    
        # Model: rectangle (length x width) extruded to height
        result = (
            cq.Workplane("XY")
            .rect(length, width)
            .extrude(height)
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00031181/gpt_generated.stl')
