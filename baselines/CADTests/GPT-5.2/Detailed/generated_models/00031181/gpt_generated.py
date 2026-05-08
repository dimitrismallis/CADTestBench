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
        # CadQuery uses millimeters by default; convert meters -> mm
        length = 0.61135 * 1000.0  # mm
        width  = 0.36026 * 1000.0  # mm
        height = 0.33843 * 1000.0  # mm
    
        result = cq.Workplane("XY").box(length, width, height, centered=True)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00031181/gpt_generated.stl')
