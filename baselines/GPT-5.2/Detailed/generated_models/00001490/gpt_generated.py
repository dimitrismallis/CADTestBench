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
        height = 0.48649
        radius = 0.75
        cutout_diameter = 0.243243243243244
    
        result = (
            cq.Workplane("XY")
            .cylinder(height, radius)
            .faces(">Z")
            .workplane()
            .hole(cutout_diameter)
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00001490/gpt_generated.stl')
