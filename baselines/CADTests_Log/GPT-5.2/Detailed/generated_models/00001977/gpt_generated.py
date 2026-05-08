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
        base = 0.20312
        height = 0.20312
        extrude_h = 0.75
    
        # Right triangle in XY: (0,0) -> (base,0) -> (0,height)
        tri = (
            cq.Workplane("XY")
            .polyline([(0, 0), (base, 0), (0, height)])
            .close()
            .extrude(extrude_h)
        )
    
        # Rotate -90 degrees about Y axis (global), around origin
        result = tri.rotate((0, 0, 0), (0, 1, 0), -90)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00001977/gpt_generated.stl')
