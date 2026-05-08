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
        height = 0.75
        outer_d = 0.85714
        inner_d = 0.535714
    
        outer_r = outer_d / 2.0
        inner_r = inner_d / 2.0
    
        # Build hollow cylinder (tube)
        result = (
            cq.Workplane("XY")
            .circle(outer_r)
            .extrude(height)
            .faces(">Z")
            .workplane()
            .circle(inner_r)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00004495/gpt_generated.stl')
