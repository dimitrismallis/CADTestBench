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
        page_len = 0.46077   # along Y (spine direction)
        page_w   = 0.75      # along X (page width away from spine)
        page_t   = 0.048077  # along Z (thickness)
    
        # Open angle between the two covers/pages (obtuse)
        open_angle_deg = 120.0
        half_angle = open_angle_deg / 2.0
    
        # --- Build one "page" with its spine edge on the Y axis (x=0) ---
        # Make a box centered in Y and Z, but starting at x=0 and extending to +X.
        # This ensures the spine is exactly the edge at x=0.
        page = (
            cq.Workplane("XY")
            .box(page_w, page_len, page_t, centered=(False, True, True))
            .translate((0, 0, page_t / 2.0))  # put bottom on Z=0 for a nicer reference
        )
    
        # --- Create left and right halves by rotating about the spine line (Y axis at x=0,z=0) ---
        # Rotate around global Y axis passing through origin.
        left = page.rotate((0, 0, 0), (0, 1, 0), +half_angle)
        right = page.rotate((0, 0, 0), (0, 1, 0), -half_angle)
    
        # Union them: they should touch only along the spine edge.
        book = left.union(right)
    
        return book
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00681053/gpt_generated.stl')
