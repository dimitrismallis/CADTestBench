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
        pts = [(0.6147, 0.0), (1.500795, 0.0), (0.886095, 0.354438), (0.0, 0.354438)]
        height = 0.425326
    
        hole_w = 0.306589
        hole_h = 0.25874
    
        # --- Base parallelogram prism ---
        base = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(height)
        )
    
        # --- Centered rectangular through-hole ---
        result = (
            base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(hole_w, hole_h, centered=True)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00039365/gpt_generated.stl')
