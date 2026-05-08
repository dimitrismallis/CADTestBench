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
        # Parameters (units as given in prompt)
        length = 0.75
        width = 0.4
        height = 0.2375
        hole_d = 0.11875
    
        result = (
            cq.Workplane("XY")
            .rect(length, width)
            .extrude(height)
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .hole(hole_d)
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00670334/gpt_generated.stl')
