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
        height = 0.00656
        outer_diameter = 1.5
        offset = 0.203459
    
        inner_diameter = outer_diameter - 2.0 * offset
        if inner_diameter <= 0:
            raise ValueError("Computed inner diameter must be positive.")
    
        outer_r = outer_diameter / 2.0
        inner_r = inner_diameter / 2.0
        half_h = height / 2.0
    
        # Build annular profile on YZ plane (normal is +X), then extrude symmetrically about that plane
        ring = (
            cq.Workplane("YZ")
            .circle(outer_r)
            .circle(inner_r)
            .extrude(half_h)                      # +X half
            .faces("<X").workplane()              # go to the -X face
            .circle(outer_r)
            .circle(inner_r)
            .extrude(half_h)                      # extend further in -X direction from that face
        )
    
        return ring
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00680715/gpt_generated.stl')
