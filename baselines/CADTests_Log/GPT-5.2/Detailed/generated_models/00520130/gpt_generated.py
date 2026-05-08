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
        main_L = 1.05
        main_W = 0.375
        main_H = 0.9
    
        tab_L = 0.6
        tab_W = 0.15
        tab_H = 0.9
    
        # Main block (centered on origin)
        part = cq.Workplane("XY").box(main_L, main_W, main_H, centered=True)
    
        # Left side protrusion (on -X face, extrude outward => negative X direction)
        part = (
            part.faces("<X")
            .workplane(centerOption="CenterOfMass")
            .rect(tab_W, tab_H)          # on YZ plane: width along Y, height along Z
            .extrude(tab_L, combine=True)
        )
    
        # Right side protrusion (on +X face, extrude outward => positive X direction)
        part = (
            part.faces(">X")
            .workplane(centerOption="CenterOfMass")
            .rect(tab_W, tab_H)          # on YZ plane: width along Y, height along Z
            .extrude(tab_L, combine=True)
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00520130/gpt_generated.stl')
