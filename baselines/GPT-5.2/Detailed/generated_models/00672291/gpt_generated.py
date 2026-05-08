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
        # Parameters (as given)
        main_length = 0.75   # vertical leg length in sketch (Y)
        main_width  = 0.015  # leg thickness in sketch
        height_3d   = 0.3    # extrusion distance (+Z)
    
        ext_width   = 0.15   # top extension length in sketch (X)
        ext_height  = main_width  # top extension thickness in sketch
    
        # Build a single closed L-shaped profile (counter-clockwise)
        # Coordinates define the outer boundary of the L:
        # (0,0) -> (main_width,0) -> (main_width, main_length-ext_height)
        # -> (ext_width, main_length-ext_height) -> (ext_width, main_length)
        # -> (0, main_length) -> back to (0,0)
        l_profile = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(main_width, 0)
            .lineTo(main_width, main_length - ext_height)
            .lineTo(ext_width, main_length - ext_height)
            .lineTo(ext_width, main_length)
            .lineTo(0, main_length)
            .close()
        )
    
        bracket = l_profile.extrude(height_3d)
        return bracket
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00672291/gpt_generated.stl')
