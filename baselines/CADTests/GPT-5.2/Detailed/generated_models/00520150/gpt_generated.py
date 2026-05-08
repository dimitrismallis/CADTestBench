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
        # Dimensions (units as given)
        length = 0.75
        width = 0.75
        height = 0.1875
    
        # Define an L shape by removing a quadrant from a square:
        # Outer: 0.75 x 0.75
        # Inner cutout: 0.375 x 0.375 located at the top-right corner
        cut = 0.375
    
        l_shape = (
            cq.Workplane("XY")
            .rect(length, width)
            .extrude(height)
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .center(length/4, width/4)  # shift to top-right quadrant relative to center
            .rect(cut, cut)
            .cutBlind(height)
        )
    
        return l_shape
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00520150/gpt_generated.stl')
