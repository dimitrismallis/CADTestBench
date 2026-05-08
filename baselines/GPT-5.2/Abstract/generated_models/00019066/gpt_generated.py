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
        width = 40.0
        length = 1.5 * width          # rectangle length
        base_thickness = 2.0          # "marginally extruded" plate
    
        rod_height = 3.0 * length     # rod height requirement
        rod_x = 4.0                   # very small rod footprint
        rod_y = 4.0
    
        # Base plate centered on origin
        base = cq.Workplane("XY").rect(length, width).extrude(base_thickness)
    
        # Add rod on top face, positioned at one corner of the top surface
        # Corner coordinates for a centered rectangle: (±length/2, ±width/2)
        rod = (
            base.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .center(length / 2 - rod_x / 2, width / 2 - rod_y / 2)
            .rect(rod_x, rod_y)
            .extrude(rod_height, combine=True)
        )
    
        return rod
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00019066/gpt_generated.stl')
