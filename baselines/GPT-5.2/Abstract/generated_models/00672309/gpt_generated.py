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
        # --- Parameters ---
        R_outer = 20.0          # outer radius of cylinder
        R_hole = R_outer * 0.5  # inner hole radius (about half)
        H = 12.0                # cylinder height
    
        channel_w = 6.0         # square channel width (X)
        channel_h = 6.0         # square channel height (Y)
        # Place square so its inner edge is slightly inside the cylinder,
        # and its outer edge extends beyond, ensuring it "connects" to the rim.
        channel_center_x = R_outer - channel_w / 2.0 + 0.5  # +0.5mm overlap into rim
    
        # --- Model ---
        result = (
            cq.Workplane("XY")
            # Base cylinder
            .circle(R_outer)
            .extrude(H)
            # Center hole (cut through)
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .circle(R_hole)
            .extrude(-H, combine="cut")
            # Side channel (square cut through full height)
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(channel_center_x, 0)
            .rect(channel_w, channel_h)
            .extrude(-H, combine="cut")
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00672309/gpt_generated.stl')
