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
        # --- Parameters (mm) ---
        pipe_length = 60.0
    
        inner_d = 20.0          # inner diameter (bore)
        wall_thk = 2.0          # pipe wall thickness
        outer_d = inner_d + 2.0 * wall_thk
    
        flange_thk = 1.0        # very thin flange thickness
        flange_outer_d = outer_d + 12.0  # flange OD larger than pipe OD
    
        # --- Build pipe as requested: positive extrusion for inner circle,
        #     negative extrusion for outer circle (cut) ---
        # Start with inner solid cylinder
        part = cq.Workplane("XY").circle(inner_d / 2.0).extrude(pipe_length)
    
        # Cut the outer circle to leave only the annular wall (hollow pipe)
        # (This removes everything outside the outer diameter.)
        part = part.faces(">Z").workplane().circle(outer_d / 2.0).cutThruAll()
    
        # --- Add thin flange at one end (top end) ---
        # Add a thin ring (larger OD) and keep it hollow by cutting the bore
        flange = (
            cq.Workplane("XY")
            .workplane(offset=pipe_length)  # at top end of pipe
            .circle(flange_outer_d / 2.0)
            .extrude(flange_thk)
            .faces(">Z").workplane()
            .circle(inner_d / 2.0)
            .cutThruAll()
        )
    
        final_result = part.union(flange)
        return final_result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00039012/gpt_generated.stl')
