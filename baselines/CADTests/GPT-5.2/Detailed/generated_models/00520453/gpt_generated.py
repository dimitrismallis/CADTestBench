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
        base_len = 0.95149
        tri_height = 0.15482
        extrude_h = 0.11183
    
        # Define an isosceles triangle with base centered on X axis at y=0
        p1 = (-base_len / 2.0, 0.0)
        p2 = ( base_len / 2.0, 0.0)
        p3 = (0.0, tri_height)
    
        result = (
            cq.Workplane("XY")
            .polyline([p1, p2, p3])
            .close()
            .extrude(extrude_h)
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00520453/gpt_generated.stl')
