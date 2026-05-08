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
        # Parameters (mm, as-is from prompt)
        extrude_len   = 0.75
        mid_length    = 0.234841
        bottom_length = 0.11742
        mid_height    = 0.280088  # provided but not used in the point definitions
        top_height    = 0.204477
        bottom_height = 0.279461
        mid_shift     = 0.004644
        bottom_shift  = 0.002349
    
        # Define vertices of the irregular pentagon
        top_vertex = (0.0, top_height)
        mid_left   = (-mid_length / 2.0 + mid_shift, 0.0)
        bot_left   = (-bottom_length / 2.0 + bottom_shift, -bottom_height)
        bot_right  = ( bottom_length / 2.0 + bottom_shift, -bottom_height)
        mid_right  = ( mid_length / 2.0 + mid_shift, 0.0)
    
        pts = [top_vertex, mid_left, bot_left, bot_right, mid_right]
    
        # Create prism
        prism = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(extrude_len)
        )
    
        return prism
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00998398/gpt_generated.stl')
