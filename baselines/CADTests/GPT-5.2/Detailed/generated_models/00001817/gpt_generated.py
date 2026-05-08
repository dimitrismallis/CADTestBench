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
        top_L = 1.20302
        top_W = 0.55872
        top_H = 0.020134
    
        leg_S = 0.060403  # square side length (X and Y)
        leg_H = 0.75
    
        # Corner offsets for leg centers (keep legs flush to top edges)
        x_off = top_L / 2 - leg_S / 2
        y_off = top_W / 2 - leg_S / 2
        leg_pts = [( x_off,  y_off),
                   ( x_off, -y_off),
                   (-x_off,  y_off),
                   (-x_off, -y_off)]
    
        # --- Model ---
        table = cq.Workplane("XY").box(top_L, top_W, top_H, centered=True)
    
        # Create legs from the bottom face of the tabletop, extruding downward
        table = (
            table
            .faces("<Z").workplane(centerOption="CenterOfMass")
            .pushPoints(leg_pts)
            .rect(leg_S, leg_S)
            .extrude(-leg_H, combine=True)
        )
    
        return table
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00001817/gpt_generated.stl')
