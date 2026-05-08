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
        base_size = 1.5
        height = 0.023438
        margin_each_side = 0.05625  # reduction on each side
    
        top_size = base_size - 2 * margin_each_side
        if top_size <= 0:
            raise ValueError("Top square size must be positive; check margin_each_side vs base_size.")
    
        # Base square extrude
        result = (
            cq.Workplane("XY")
            .rect(base_size, base_size)
            .extrude(height)
            # Top smaller square extrude on top face
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .rect(top_size, top_size)
            .extrude(height)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00676218/gpt_generated.stl')
