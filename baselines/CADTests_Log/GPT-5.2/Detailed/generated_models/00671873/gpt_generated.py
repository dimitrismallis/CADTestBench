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
        # Dimensions (units as given)
        base_len = 0.75
        base_w   = 0.658737
        base_h   = 0.284211
    
        step_len = 0.347368
        step_h   = 0.135789
    
        total_h = base_h + step_h
    
        # Create side profile on XZ plane:
        # Base rectangle: x in [0, base_len], z in [0, base_h]
        # Upper step:     x in [0, step_len], z in [base_h, total_h]
        profile = (
            cq.Workplane("XZ")
            .moveTo(0, 0)
            .lineTo(base_len, 0)
            .lineTo(base_len, base_h)
            .lineTo(step_len, base_h)
            .lineTo(step_len, total_h)
            .lineTo(0, total_h)
            .close()
        )
    
        # Extrude along Y to constant width
        result = profile.extrude(base_w)
    
        # Center the solid about Y=0 for nicer placement (optional but common)
        result = result.translate((0, -base_w / 2.0, 0))
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00671873/gpt_generated.stl')
