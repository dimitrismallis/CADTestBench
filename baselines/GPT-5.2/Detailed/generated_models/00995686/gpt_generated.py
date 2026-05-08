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
        od = 0.702675
        wall = 0.049281
        width = 0.75
    
        ro = od / 2.0
        ri = ro - wall
        if ri <= 0:
            raise ValueError("Wall thickness too large for given outer diameter.")
    
        # --- Base tube (hollow cylinder) ---
        tube = (
            cq.Workplane("XY")
            .circle(ro)
            .circle(ri)
            .extrude(width)  # along +Z
        )
    
        # --- Cutting box: OD x OD in X/Y, and same width in Z ---
        # Place it so it intersects the tube and removes a sector.
        # Shift in +X so it cuts away a "side" segment rather than splitting in half.
        cut_box = (
            cq.Workplane("XY")
            .center(ro * 0.65, 0)          # adjust to control how much of the pipe is removed
            .rect(od, od)
            .extrude(width)
        )
    
        result = tube.cut(cut_box)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00995686/gpt_generated.stl')
