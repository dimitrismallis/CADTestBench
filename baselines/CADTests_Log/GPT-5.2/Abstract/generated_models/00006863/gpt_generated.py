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
        width = 40.0
        height = 25.0
        thickness = 10.0
    
        # Rectangle sketch extruded into a solid
        result = (
            cq.Workplane("XY")
            .rect(width, height)
            .extrude(thickness)
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00006863/gpt_generated.stl')
