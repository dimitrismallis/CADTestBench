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
        inner_width = 40.0          # clear span between inner faces of legs
        inner_height = 30.0         # clear height under the top bridge
        top_thk = 5.0               # thickness of the horizontal section (bridge)
        leg_thk = 2.0 * top_thk     # upright columns are twice the width of horizontal section
        depth = 20.0                # extrusion depth (table "length" into the screen)
    
        hole_d = 6.0                # small circular hole diameter
    
        # Derived overall size of the U profile
        outer_width = inner_width + 2.0 * leg_thk
        outer_height = inner_height + top_thk
    
        # --- Build U-shaped face by subtracting inner rectangle from outer rectangle ---
        u_face = (
            cq.Workplane("XY")
            .rect(outer_width, outer_height)
            .rect(inner_width, inner_height)   # second rect becomes an inner wire
            .extrude(depth)                    # extrude with hole (inner wire) -> U-shaped solid
        )
    
        # --- Hole through the top horizontal surface (centered) ---
        result = (
            u_face
            .faces(">Z")                       # top face of the extruded solid
            .workplane(centerOption="CenterOfMass")
            .hole(hole_d)                      # through-hole by default
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00996001/gpt_generated.stl')
