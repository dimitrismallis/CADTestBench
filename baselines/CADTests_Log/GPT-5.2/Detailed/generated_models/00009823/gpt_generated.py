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
        side_len = 1.5
        height = 0.016238
    
        # For a regular hexagon, circumradius R = side length s
        R = side_len
        diameter = 2 * R
    
        result = (
            cq.Workplane("XY")
            .polygon(6, diameter)
            .extrude(height)
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00009823/gpt_generated.stl')
