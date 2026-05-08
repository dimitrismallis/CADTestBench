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
        # Parameters (units as given)
        height = 0.26068
        outer_d = 1.5
        offset_each_side = 0.013033  # reduction from both sides of outer diameter
    
        outer_r = outer_d / 2.0
        inner_d = outer_d - 2.0 * offset_each_side
        inner_r = inner_d / 2.0
    
        # Create ring (cylindrical annulus) extruded along +Z first
        ring = (
            cq.Workplane("XY")
            .circle(outer_r)
            .circle(inner_r)
            .extrude(height)
        )
    
        # Re-orient so the cylinder axis is along global Y (i.e., "extruded along the y-axis")
        # Rotating +90° about X maps Z -> Y.
        ring_y = ring.rotate((0, 0, 0), (1, 0, 0), 90)
    
        return ring_y
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00670279/gpt_generated.stl')
