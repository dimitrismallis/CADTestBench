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
        d = 0.375
        r = d / 2.0
        h = 0.691189
        top_len = 0.208765
    
        # --- Base solid: cylinder, base at Z=0 ---
        cyl = cq.Workplane("XY").cylinder(h, r, centered=(True, True, False))
    
        # --- Cutting solid (triangular prism) ---
        # Triangle in XZ plane:
        # (-r,0) -> (r,0) -> (x_top,h)
        x_top = -r + top_len
        y_span = 2.5 * r  # oversize to guarantee full span across cylinder
    
        cutter = (
            cq.Workplane("XZ")
            .moveTo(-r, 0)
            .lineTo(r, 0)
            .lineTo(x_top, h)
            .close()
            .extrude(y_span)                 # extrudes in +Y from the XZ plane
            .translate((0, -y_span / 2, 0))  # center it about Y=0
        )
    
        sliced = cyl.cut(cutter)
    
        # --- Final positioning: ensure base sits on Z=0 ---
        bb = sliced.val().BoundingBox()
        result = sliced.translate((0, 0, -bb.zmin))
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00036518/gpt_generated.stl')
