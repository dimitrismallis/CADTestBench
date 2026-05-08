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
        # --- Parameters ---
        plate_thk = 6.0
    
        # Irregular rhombus-like quadrilateral vertices in XY
        pts = [
            (-35.0, 0.0),
            (-5.0, 22.0),
            (40.0, 6.0),
            (10.0, -18.0),
        ]
    
        # Rectangular prism ("handle") dimensions
        handle_len = 45.0   # sticks out from the chosen side face
        handle_w   = 18.0   # in-plane width on that face
        handle_h   = 16.0   # in-plane height on that face (Z direction)
    
        # --- Base: extruded irregular rhombus ---
        plate = (
            cq.Workplane("XY")
            .moveTo(*pts[0])
            .lineTo(*pts[1])
            .lineTo(*pts[2])
            .lineTo(*pts[3])
            .close()
            .extrude(plate_thk)
        )
    
        # --- Attach rectangular prism to the center of one extruded edge (a side face) ---
        # Select the side face at maximum X and build the prism from its center.
        result = (
            plate
            .faces(">X")
            .workplane(centerOption="CenterOfMass")
            .rect(handle_w, handle_h)
            .extrude(handle_len, combine=True)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00999374/gpt_generated.stl')
