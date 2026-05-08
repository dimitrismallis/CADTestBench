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
        main_d = 60.0          # diameter of the large cylinder
        main_h = 20.0          # height (length) of the large cylinder
    
        small_d = main_d / 2.0
        small_h = main_h * 5.0
    
        # Main cylinder (extruded upward from XY plane)
        result = cq.Workplane("XY").circle(main_d / 2.0).extrude(main_h)
    
        # Smaller, longer cylinder on the bottom face, extruded downward
        result = (
            result
            .faces("<Z").workplane(centerOption="CenterOfMass")
            .circle(small_d / 2.0)
            .extrude(-small_h)  # negative to go downward from the bottom face
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00521217/gpt_generated.stl')
