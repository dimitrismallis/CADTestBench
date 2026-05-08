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
        # Parameters
        outer_radius = 20.0
        thickness = 3.0
        hole_radius = outer_radius / 2.0
    
        # Disk, then centered hole
        result = (
            cq.Workplane("XY")
            .circle(outer_radius)
            .extrude(thickness)
            .faces(">Z")
            .workplane()
            .hole(2 * hole_radius)  # hole() takes diameter
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00670817/gpt_generated.stl')
