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
        D1 = 80.0          # main cylinder diameter
        H1 = 200.0         # main cylinder height (long)
    
        D2 = D1 / 4.0      # 1/4 diameter of first
        H2 = H1 / 8.0      # 1/8 height of first
    
        D3 = D2 / 2.0      # 1/2 diameter of second
        H3 = H2 * 2.0      # twice height of second
    
        # Offset "slightly below the center" on the circular base (negative Y)
        offset_y = -D1 * 0.15
    
        # --- Model ---
        main = cq.Workplane("XY").cylinder(H1, D1 / 2.0)
    
        # Add second cylinder protruding from the top base of the main cylinder
        second = (
            main.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .center(0, offset_y)
            .cylinder(H2, D2 / 2.0, centered=(True, True, False))  # start at base, go outward +Z
        )
    
        # Add third cylinder, concentric with the second, protruding further outward
        third = (
            second.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .center(0, offset_y)
            .cylinder(H3, D3 / 2.0, centered=(True, True, False))
        )
    
        return third
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00670268/gpt_generated.stl')
