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
        base_h = 0.681818
        base_d = 0.681818
        base_r = base_d / 2.0
    
        top_h = 0.252273
        top_d = 1.5
        top_r = top_d / 2.0
    
        # Base cylinder (extruded circle)
        result = (
            cq.Workplane("XY")
            .circle(base_r)
            .extrude(base_h)
            # Larger circle near the top: place sketch on the top face and extrude upward
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .circle(top_r)
            .extrude(top_h)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00982481/gpt_generated.stl')
