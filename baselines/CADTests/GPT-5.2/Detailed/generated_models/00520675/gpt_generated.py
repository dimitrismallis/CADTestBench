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
        h = 0.6
        d = 1.5
        t = 0.075
    
        result = (
            cq.Workplane("XY")
            .cylinder(h, d / 2.0)          # centered at origin by default
            .faces(">Z")
            .shell(-t)                     # inward shell, open at top face
            .translate((0, 0, h / 2.0))    # move so base is on Z=0, centered at origin
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00520675/gpt_generated.stl')
