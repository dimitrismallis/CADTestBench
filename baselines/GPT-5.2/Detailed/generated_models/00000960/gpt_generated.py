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
        base_L = 0.75
        base_W = 0.75
        h = 0.00195
    
        tab_L = 0.281257
        tab_W = 0.0625
    
        # Base rectangle (thin plate), centered at origin
        base = cq.Workplane("XY").box(base_L, base_W, h, centered=True)
    
        # Second rectangle (tab), also centered, then translated into position
        # Connect to right edge of base: base right face at x = +base_L/2
        # Tab left face at x = tab_center_x - tab_L/2 => set equal to +base_L/2
        tab_center_x = (base_L / 2.0) + (tab_L / 2.0)
    
        # "Starting halfway up its height" interpreted as halfway up the base's width in +Y direction:
        # base top edge at y=+base_W/2, halfway up from center => y=+base_W/4
        tab_center_y = base_W / 4.0
    
        tab = (
            cq.Workplane("XY")
            .box(tab_L, tab_W, h, centered=True)
            .translate((tab_center_x, tab_center_y, 0))
        )
    
        result = base.union(tab)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00000960/gpt_generated.stl')
