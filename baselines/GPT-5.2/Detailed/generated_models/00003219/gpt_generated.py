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
        height = 1.23718
        radius = 0.27226
    
        # Cylinder axis along +Z, base on XY plane at Z=0
        result = cq.Workplane("XY").circle(radius).extrude(height)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00003219/gpt_generated.stl')
