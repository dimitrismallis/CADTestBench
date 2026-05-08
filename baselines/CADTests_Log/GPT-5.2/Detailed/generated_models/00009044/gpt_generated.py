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
        height = 0.375
        outer_diameter = 1.5
        cutout_diameter = 0.237219
    
        result = (
            cq.Workplane("XY")
            .cylinder(height, outer_diameter / 2.0)
            .faces(">Z").workplane()
            .hole(cutout_diameter)
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00009044/gpt_generated.stl')
