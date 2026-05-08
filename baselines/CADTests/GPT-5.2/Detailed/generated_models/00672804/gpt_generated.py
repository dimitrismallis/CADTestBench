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
        side = 1.5
        height = 0.1125
        hole_d = 0.15
    
        result = (
            cq.Workplane("XY")
            .rect(side, side)
            .extrude(height)
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .hole(hole_d)
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00672804/gpt_generated.stl')
