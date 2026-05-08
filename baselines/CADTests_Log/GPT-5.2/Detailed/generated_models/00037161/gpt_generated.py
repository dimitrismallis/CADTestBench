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
        plate_len = 1.5
        plate_wid = 1.5
        plate_h   = 0.0255
    
        cut_len = 0.12
        cut_wid = 0.24
    
        # Base plate centered on origin, thickness in Z
        result = (
            cq.Workplane("XY")
            .box(plate_len, plate_wid, plate_h, centered=(True, True, False))
            .faces(">Z").workplane()
            .rect(cut_len, cut_wid)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00037161/gpt_generated.stl')
