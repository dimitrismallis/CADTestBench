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
        side = 20.0                 # mm
        height = 2.0 * side          # extrusion length
    
        result = (
            cq.Workplane("XY")
            .rect(side, side)
            .extrude(height)
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00520974/gpt_generated.stl')
