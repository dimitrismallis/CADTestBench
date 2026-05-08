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
        base_d = 1.5
        base_h = 0.114796
    
        top_d = 1.17857
        top_h = 0.306123
    
        # Base cylinder (extrude a circle)
        base = cq.Workplane("XY").circle(base_d / 2).extrude(base_h)
    
        # Top cylinder, translated up by base height
        top = (
            cq.Workplane("XY")
            .circle(top_d / 2)
            .extrude(top_h)
            .translate((0, 0, base_h))
        )
    
        # Combine
        result = base.union(top)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00004935/gpt_generated.stl')
