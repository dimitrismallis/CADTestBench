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
        length = 80.0          # X
        base_width = 40.0      # Y
        tier_width = 24.0      # Y (smaller, same length)
        height = 15.0          # Z for each tier
        hole_d = 12.0
    
        # Place the upper tier at one end of the base in Y (like a step)
        # Base is centered at Y=0, so its +Y edge is at +base_width/2.
        # Put the tier centered at Y = +base_width/2 - tier_width/2 so it sits on the +Y end.
        tier_center_y = (base_width / 2.0) - (tier_width / 2.0)
    
        # --- Model ---
        base = cq.Workplane("XY").box(length, base_width, height, centered=True)
    
        tier = (
            cq.Workplane("XY")
            .workplane(offset=height / 2.0)  # move to top face of base (Z = +height/2)
            .center(0, tier_center_y)
            .rect(length, tier_width)
            .extrude(height, combine=True)   # extrude upward by same amount
        )
    
        stepped = base.union(tier)
    
        # Hole through both tiers, centered on the upper block
        result = (
            stepped
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(0, tier_center_y)  # center of the upper tier in XY
            .hole(hole_d)              # through-hole (cuts thru all by default)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00998843/gpt_generated.stl')
