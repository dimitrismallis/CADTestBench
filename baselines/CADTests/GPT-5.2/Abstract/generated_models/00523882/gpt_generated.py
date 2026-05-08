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
        # Base (taller) trapezoid prism
        h1 = 30.0          # trapezoid height in Y
        w1_bottom = 60.0   # bottom width in X
        w1_top = 35.0      # top width in X
        z1 = 25.0          # main extrusion height (substantial)
    
        # Attached (shallower) trapezoid prism - slightly larger profile, much less extruded
        h2 = h1 + 6.0
        w2_bottom = w1_bottom + 10.0
        w2_top = w1_top + 10.0
        z2 = 6.0           # much less extruded than z1
    
        # --- Helper: right trapezoid wire (right side vertical) ---
        # Points are defined CCW:
        # (0,0) -> (bottom width,0) -> (bottom width, height) -> (bottom width - top width, height) -> close
        def right_trapezoid(w_bottom: float, w_top: float, h: float) -> cq.Workplane:
            dx = w_bottom - w_top
            return (
                cq.Workplane("XY")
                .moveTo(0, 0)
                .lineTo(w_bottom, 0)
                .lineTo(w_bottom, h)
                .lineTo(dx, h)
                .close()
            )
    
        # --- Base solid ---
        base = right_trapezoid(w1_bottom, w1_top, h1).extrude(z1)
    
        # --- Attached shallow solid on +X side face of base ---
        # Use the +X face as a workplane; extrude outward (+X) by z2.
        # Center the larger trapezoid on that face in Y and Z.
        attach = (
            base
            .faces(">X").workplane(centerOption="CenterOfMass")
            .moveTo(0, 0)  # local 2D coords on that face
            .moveTo(-w2_bottom/2, -h2/2)  # shift so trapezoid is centered about the face origin
            .lineTo(w2_bottom/2, -h2/2)
            .lineTo(w2_bottom/2, h2/2)
            .lineTo(w2_bottom/2 - w2_top, h2/2)
            .close()
            .extrude(z2, combine=True)
        )
    
        return attach
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00523882/gpt_generated.stl')
