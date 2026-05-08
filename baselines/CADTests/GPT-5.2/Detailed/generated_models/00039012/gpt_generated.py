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
        inch = 25.4
    
        # Given dimensions (inches -> mm)
        inner_d = 0.70248 * inch
        flange_outer_d = 0.825 * inch
    
        pipe_h = 0.75 * inch
        flange_h = 0.01125 * inch
    
        # Choose a reasonable pipe outer diameter so the part is physically valid.
        # The prompt only specifies the inner diameter and the flange outer diameter.
        # We'll make the pipe OD slightly smaller than the flange OD.
        pipe_outer_d = 0.78 * inch  # < flange_outer_d, > inner_d
    
        # Main pipe: outer cylinder extrude, then cut inner bore
        pipe = (
            cq.Workplane("XY")
            .circle(pipe_outer_d / 2)
            .extrude(pipe_h)
            .faces(">Z").workplane()
            .circle(inner_d / 2)
            .cutThruAll()
        )
    
        # Thin flange at base: larger OD disk, same inner bore, very thin height
        flange = (
            cq.Workplane("XY")
            .circle(flange_outer_d / 2)
            .extrude(flange_h)
            .faces(">Z").workplane()
            .circle(inner_d / 2)
            .cutThruAll()
        )
    
        final_result = pipe.union(flange)
        return final_result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00039012/gpt_generated.stl')
