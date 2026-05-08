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
        length = 1.5
        width = 1.02857
        height = 0.17143
    
        hole_d = 0.095635
        inset_len = 0.263507
        inset_wid = 0.219429
    
        # Compute spacing between hole centers (construction rectangle size)
        hole_center_rect_len = length - 2 * inset_len
        hole_center_rect_wid = width - 2 * inset_wid
    
        # Base prism + 4 corner-inset holes on top face
        result = (
            cq.Workplane("XY")
            .box(length, width, height, centered=True)
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .rect(hole_center_rect_len, hole_center_rect_wid, forConstruction=True)
            .vertices()
            .hole(hole_d)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00006578/gpt_generated.stl')
