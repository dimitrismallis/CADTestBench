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
        length = 0.1875   # X
        width  = 0.1875   # Y
        height = 0.75     # Z extrusion height
    
        pad = 0.014063    # wall thickness on each side
    
        inner_length = length - 2 * pad
        inner_width  = width  - 2 * pad
        if inner_length <= 0 or inner_width <= 0:
            raise ValueError("Padding too large: inner dimensions became non-positive.")
    
        # Outer solid
        outer = cq.Workplane("XY").box(length, width, height, centered=True)
    
        # Inner cut (through all to ensure a clean pipe)
        pipe = (
            outer
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(inner_length, inner_width)
            .cutThruAll()
        )
    
        # Rotate 90 degrees about X-axis (around global origin)
        pipe = pipe.rotate((0, 0, 0), (1, 0, 0), 90)
    
        return pipe
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00670256/gpt_generated.stl')
