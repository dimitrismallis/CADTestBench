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
        cyl_diameter = 120.0   # very large diameter
        cyl_height   = 12.0    # short cylinder
        cutout_d     = 10.0    # small circular cutout at center
    
        result = (
            cq.Workplane("XY")
            .cylinder(cyl_height, cyl_diameter / 2.0)
            .faces(">Z").workplane()
            .hole(cutout_d)  # through-hole cutout at center
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00009044/gpt_generated.stl')
