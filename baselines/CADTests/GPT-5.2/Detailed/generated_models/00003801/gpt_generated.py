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
        height = 0.09494
        outer_d = 1.5
        hole_d = 0.93038
    
        result = (
            cq.Workplane("XY")
            .circle(outer_d / 2.0)
            .extrude(height)
            .faces(">Z")
            .workplane()
            .circle(hole_d / 2.0)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00003801/gpt_generated.stl')
