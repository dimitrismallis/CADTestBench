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
        height = 1.5
        outer_d = 0.75
        inner_d = 0.3125
    
        outer_r = outer_d / 2.0
        inner_r = inner_d / 2.0
    
        # Build as a vertical tube along +Z, then rotate to horizontal
        tube = (
            cq.Workplane("XY")
            .circle(outer_r)
            .circle(inner_r)
            .extrude(height)
        )
    
        # Orient horizontally: rotate so Z axis becomes X axis
        tube_horiz = tube.rotate((0, 0, 0), (0, 1, 0), 90)
    
        return tube_horiz
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00004596/gpt_generated.stl')
