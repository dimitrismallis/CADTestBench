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
        s = 0.32592
        h = 0.023387
    
        # Build a single closed outline (irregular rhombus-like pentagon):
        # Square corners: (-s/2,-s/2) -> (s/2,-s/2) -> (s/2,s/2) -> (-s/2,s/2)
        # Triangle attached on top edge from (-s/2,s/2) to (s/2,s/2) with apex at (-s/2, s/2+s)
        pts = [
            (-s/2, -s/2),
            ( s/2, -s/2),
            ( s/2,  s/2),
            (-s/2,  s/2 + s),
            (-s/2,  s/2),
        ]
    
        profile = cq.Workplane("XY").polyline(pts).close()
    
        result = profile.extrude(h)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00672359/gpt_generated.stl')
