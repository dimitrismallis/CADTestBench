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
        main_len = 80.0   # X direction (longer)
        main_wid = 40.0   # Y direction (shorter)
        tab_len  = 20.0   # how far tabs extend outward in X
        tab_wid  = 18.0   # tab size in Y (centered on long edge midpoint)
        thickness = 12.0
    
        hole_d = 28.0
    
        # --- 2D profile: main rectangle + two side tabs ---
        # Main rectangle centered at origin
        profile = cq.Workplane("XY").rect(main_len, main_wid)
    
        # Left tab: centered on midpoint of left long edge (x = -main_len/2)
        profile = (
            profile
            .center(-main_len/2 - tab_len/2, 0)
            .rect(tab_len, tab_wid)
            .center(main_len/2 + tab_len/2, 0)  # move from left-tab center to right-tab center
            .rect(tab_len, tab_wid)
        )
    
        # Extrude the unioned wires into a solid
        solid = profile.extrude(thickness)
    
        # --- Center hole (through) ---
        solid = solid.faces(">Z").workplane(centerOption="CenterOfMass").hole(hole_d)
    
        return solid
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00997071/gpt_generated.stl')
