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
        # --- Given dimensions (units as provided) ---
        h1 = 0.75
        d1 = 0.470339
    
        h2 = 0.082627
        d2 = 0.152542
    
        h3 = 0.190678
        d3 = 0.075981
    
        padding = 0.247881  # from edge of first cylinder
    
        r1 = d1 / 2.0
        r2 = d2 / 2.0
        r3 = d3 / 2.0
    
        # Positioning:
        # - "padding from the edge" interpreted as radial inset from outer rim along +X direction.
        # - "slightly below the center" interpreted as a small negative Y offset.
        x_off = max(0.0, r1 - padding)
        y_off = -0.05 * d1  # small downward shift relative to main cylinder diameter
    
        # --- Model ---
        main = cq.Workplane("XY").circle(r1).extrude(h1)
    
        # Add 2nd cylinder on the top face, offset from center
        with_second = (
            main
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(x_off, y_off)
            .circle(r2).extrude(h2, combine=True)
        )
    
        # Add 3rd cylinder concentric with 2nd, protruding further outward from the 2nd's top
        with_third = (
            with_second
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .circle(r3).extrude(h3, combine=True)
        )
    
        # Rotate entire assembly by -90 degrees around Y-axis
        final_result = with_third.rotate((0, 0, 0), (0, 1, 0), -90)
    
        return final_result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00670268/gpt_generated.stl')
