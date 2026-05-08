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
        outer_x = 0.23077
        outer_z = 0.23077
        length_y = 0.75
    
        inside_padding = 0.023077
        inner_x = outer_x - 2 * inside_padding  # 0.184616 (≈ 0.18462)
        inner_z = outer_z - 2 * inside_padding
    
        # Outer solid: sketch on XZ plane, extrude along +Y
        outer = cq.Workplane("XZ").rect(outer_x, outer_z).extrude(length_y)
    
        # Inner cut: same center, extrude negatively along Y to cut through
        result = (
            outer
            .faces(">Y").workplane(centerOption="CenterOfMass")
            .rect(inner_x, inner_z)
            .cutBlind(-length_y)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00037494/gpt_generated.stl')
