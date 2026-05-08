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
        # Dimensions (CadQuery default units are mm; using given "units" directly)
        length = 0.3
        width = 0.7
        height = 0.3
    
        final_result = cq.Workplane("XY").box(length, width, height)
        return final_result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00003247/gpt_generated.stl')
