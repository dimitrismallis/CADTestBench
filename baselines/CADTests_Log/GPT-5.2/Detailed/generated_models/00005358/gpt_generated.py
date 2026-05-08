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
        height = 0.01463
        od = 1.5
        id_ = 1.45232
    
        outer_r = od / 2.0
        inner_r = id_ / 2.0
    
        ring = (
            cq.Workplane("XY")
            .circle(outer_r)
            .circle(inner_r)
            .extrude(height)
        )
    
        return ring
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00005358/gpt_generated.stl')
