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
        length = 1.5
        width  = 0.83721
        height = 0.07849
    
        # Centered on origin in XY, base on Z=0 (so not centered in Z)
        result = cq.Workplane("XY").box(length, width, height, centered=(True, True, False))
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00009863/gpt_generated.stl')
