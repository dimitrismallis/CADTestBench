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
        # --- Parameters (units as provided) ---
        base_L = 1.40217
        base_W = 0.062517
        base_H = 0.75
    
        mid_L = 1.27174
        mid_W = 0.103421
        mid_H = 0.75
    
        trap_bottom_w = 1.33696          # bottom width (X direction)
        trap_top_w = trap_bottom_w * 0.92  # slightly smaller than base
        trap_depth = mid_W * 1.10         # slightly longer than width of 2nd rectangle (Y direction)
        trap_H = 0.75
        trap_angle = 72  # noted, but profile is explicitly defined by top/bottom widths
    
        # --- Base block ---
        result = cq.Workplane("XY").box(base_L, base_W, base_H, centered=True)
    
        # --- Middle block on top of base ---
        result = (
            result
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(mid_L, mid_W)
            .extrude(mid_H, combine=True)
        )
    
        # --- Trapezoid on top of middle block ---
        # Define an isosceles trapezoid in the top face workplane:
        # bottom edge at y=-depth/2, top edge at y=+depth/2
        half_bot = trap_bottom_w / 2.0
        half_top = trap_top_w / 2.0
        half_depth = trap_depth / 2.0
    
        result = (
            result
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .moveTo(-half_bot, -half_depth)
            .lineTo(half_bot, -half_depth)
            .lineTo(half_top, half_depth)
            .lineTo(-half_top, half_depth)
            .close()
            .extrude(trap_H, combine=True)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00009843/gpt_generated.stl')
