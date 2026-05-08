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
        # Dimensions (units as given in prompt)
        base_size = 0.307377
        base_thickness_y = 0.012295
    
        body_length_x = 0.307377
        body_width_z = 0.184426
        body_height_y = 0.737705
    
        # Work on XZ so extrude goes along Y
        result = (
            cq.Workplane("XZ")
            .rect(base_size, base_size)                 # square in X-Z
            .extrude(base_thickness_y)                  # along +Y
            .faces(">Y").workplane(centerOption="CenterOfMass")
            .rect(body_length_x, body_width_z)          # centered smaller rectangle
            .extrude(body_height_y)                     # tall pillar body along +Y
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00522404/gpt_generated.stl')
