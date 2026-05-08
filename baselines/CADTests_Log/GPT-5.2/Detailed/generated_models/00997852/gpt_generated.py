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
        base_len = 1.5
        base_wid = 0.153061
        base_hgt = 0.918367
    
        tier_len = 1.43878
        tier_hgt = 0.841837  # interpreted as the tier's width in Y (since rectangle needs LxW on the sketch plane)
        tier_extrude = 0.229592
    
        # --- Model ---
        base = cq.Workplane("XY").box(base_len, base_wid, base_hgt, centered=True)
    
        tier = (
            base
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .rect(tier_len, tier_hgt, centered=True)
            .extrude(tier_extrude, combine=True)
        )
    
        return tier
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00997852/gpt_generated.stl')
