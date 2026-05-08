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
        base = 0.150756
        height = 1.5
        thickness = 0.188445
    
        # Define an isosceles triangle:
        # Base endpoints at (-base/2, 0) and (base/2, 0), apex at (0, height)
        p1 = (-base / 2.0, 0.0)
        p2 = ( base / 2.0, 0.0)
        p3 = (0.0, height)
    
        tri = (
            cq.Workplane("XY")
            .moveTo(*p1)
            .lineTo(*p2)
            .lineTo(*p3)
            .close()
        )
    
        result = tri.extrude(thickness)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00670466/gpt_generated.stl')
