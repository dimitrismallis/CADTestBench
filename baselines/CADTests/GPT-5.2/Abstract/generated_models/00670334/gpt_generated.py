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
        # Parameters (mm)
        length = 60.0
        width = 30.0
        height = 10.0
        hole_d = 10.0
    
        # Sketch rectangle -> extrude -> center hole
        result = (
            cq.Workplane("XY")
            .rect(length, width)
            .extrude(height)
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .hole(hole_d)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00670334/gpt_generated.stl')
