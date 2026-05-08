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
        # Parameters (units as provided)
        length = 1.5
        width = 0.004152
        height = 0.720946
        requested_fillet_r = 0.077855
    
        # Create base rectangular solid
        part = cq.Workplane("XY").box(length, width, height, centered=True)
    
        # Fillet feasibility:
        # For edges parallel to X, the fillet is constrained by the Y/Z cross-section.
        # Use a conservative clamp to avoid OCCT "NotDone" failures.
        max_r = 0.49 * min(width, height) / 2.0  # slightly under half of the smallest adjacent dimension
        fillet_r = min(requested_fillet_r, max_r)
    
        # Apply fillet to edges along the length (parallel to X)
        part = part.edges("|X").fillet(fillet_r)
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00681463/gpt_generated.stl')
