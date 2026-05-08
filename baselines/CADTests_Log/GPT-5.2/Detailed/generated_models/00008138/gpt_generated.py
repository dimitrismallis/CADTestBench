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
        height = 0.75
        outer_d = 0.07812
        inner_d = 0.046741
    
        outer_r = outer_d / 2.0
        inner_r = inner_d / 2.0
    
        # Build hollow cylinder by subtracting inner from outer
        tube = (
            cq.Workplane("XY")
            .cylinder(height, outer_r, centered=(True, True, False))
            .cut(
                cq.Workplane("XY")
                .cylinder(height, inner_r, centered=(True, True, False))
            )
            # Translate along Z by half the height
            .translate((0, 0, height / 2.0))
        )
    
        return tube
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00008138/gpt_generated.stl')
