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
        # Parameters (units as given)
        base_d = 0.567213
        base_h = 0.5625
    
        top_d = 0.266022
        top_h = 0.1875
    
        result = (
            cq.Workplane("XY")
            .circle(base_d / 2.0)
            .extrude(base_h)
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .circle(top_d / 2.0)
            .extrude(top_h)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00995843/gpt_generated.stl')
