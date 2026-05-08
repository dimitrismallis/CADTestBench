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
        # Parameters (mm)
        base_radius = 30.0
        base_height = 10.0
    
        top_radius = 24.0
        top_height = 8.0
    
        result = (
            cq.Workplane("XY")
            .circle(base_radius)
            .extrude(base_height)
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .circle(top_radius)
            .extrude(top_height)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00004935/gpt_generated.stl')
