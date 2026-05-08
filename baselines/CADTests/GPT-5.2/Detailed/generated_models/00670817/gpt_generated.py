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
        outer_d = 1.5
        height = 0.113636
        hole_d = 0.738636
    
        result = (
            cq.Workplane("XY")
            .circle(outer_d / 2.0)
            .extrude(height)
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .hole(hole_d)  # through-hole by default
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00670817/gpt_generated.stl')
