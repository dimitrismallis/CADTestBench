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
        # --- Parameters (units as given) ---
        h = 0.75
        od = 0.533654
        wall = 0.017308
        orad = od / 2.0
        irad = orad - wall
    
        tiny_d = 0.090144
        tiny_depth = 0.034616
    
        # --- Main hollow cylinder (tube), extruded along +Z from Z=0 ---
        tube = (
            cq.Workplane("XY")
            .circle(orad)
            .circle(irad)
            .extrude(h)  # annulus extrude -> hollow cylinder
        )
    
        # --- Bottom cap to close the cylinder (disk filling the inner diameter) ---
        capped = (
            tube
            .faces("<Z").workplane(centerOption="CenterOfMass")
            .circle(irad)
            .extrude(wall, combine=True)  # small thickness cap
        )
    
        # --- Tiny hollow circle in the middle of the bottom (a blind hole) ---
        final_result = (
            capped
            .faces("<Z").workplane(centerOption="CenterOfMass")
            .hole(tiny_d, depth=tiny_depth)
        )
    
        return final_result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00522355/gpt_generated.stl')
