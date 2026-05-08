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
        diameter = 1.5
        radius = diameter / 2.0
        height = 0.440903
    
        # Cylinder axis aligned with X by setting direct=(1,0,0)
        result = cq.Workplane("XY").cylinder(height=height, radius=radius, direct=(1, 0, 0))
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00670106/gpt_generated.stl')
