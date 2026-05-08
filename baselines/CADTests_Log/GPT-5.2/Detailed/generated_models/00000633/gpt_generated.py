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
        # Dimensions (units as provided)
        length = 0.75
        width = 0.1875
        height = 0.00391
        hole_d = 0.12512
    
        result = (
            cq.Workplane("XY")
            .box(length, width, height, centered=True)
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .hole(hole_d)
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00000633/gpt_generated.stl')
