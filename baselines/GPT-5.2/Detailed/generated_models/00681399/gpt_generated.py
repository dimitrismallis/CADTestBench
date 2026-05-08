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
        block_len = 0.990099
        block_wid = 0.415842
        block_h   = 0.990099
    
        hole_d = 0.471867
    
        pipe_id = hole_d
        pipe_od = 0.517113
        pipe_h  = 0.334158
    
        translate_vec = (0.0, -0.207921, 0.025308)
    
        # Base block
        part = (
            cq.Workplane("XY")
            .box(block_len, block_wid, block_h, centered=True)
        )
    
        # Cut hole from top face (through all)
        part = (
            part
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .hole(hole_d)
        )
    
        # Add annular pipe on top face
        part = (
            part
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .circle(pipe_od / 2.0)
            .circle(pipe_id / 2.0)
            .extrude(pipe_h, combine=True)
        )
    
        # Translate entire assembly
        part = part.translate(translate_vec)
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00681399/gpt_generated.stl')
