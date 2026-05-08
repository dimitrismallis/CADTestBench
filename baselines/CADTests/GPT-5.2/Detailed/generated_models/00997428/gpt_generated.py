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
        outer_d = 0.503822
        outer_r = outer_d / 2.0
        height = 0.75
    
        inner_d = 0.426316
        inner_r = inner_d / 2.0
        inner_cut_depth = 0.710526  # cut downward from the top, not thru all
    
        rod_d = 0.05921
        rod_r = rod_d / 2.0
        rod_len = 0.631579
    
        top_margin = 0.049342  # distance from top edge down to rod centerline
    
        # Outer cylinder (bucket body)
        body = cq.Workplane("XY").circle(outer_r).extrude(height)
    
        # Hollow cut: start from top face and cut downward by inner_cut_depth
        body = (
            body
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .circle(inner_r)
            .cutBlind(-inner_cut_depth)
        )
    
        # Horizontal rod: cylinder along X, centered through the bucket
        rod_z = height - top_margin
        rod = (
            cq.Workplane("YZ", origin=(0, 0, rod_z))
            .circle(rod_r)
            .extrude(rod_len, both=True)  # along +/-X
        )
    
        result = body.union(rod)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00997428/gpt_generated.stl')
