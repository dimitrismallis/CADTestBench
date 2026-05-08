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
        plate_L = 0.75
        plate_W = 0.605769
        thickness = 0.018035
    
        trap_base = 0.375
        side_len = 0.028846
        base_angle_deg = 45.0
    
        # Slight right shift of trapezoid center relative to plate short-edge center
        x_shift = 0.03  # "slightly to the right" (tunable)
    
        # --- Derived trapezoid geometry ---
        # Height from side length and base angle (angle between base and side)
        h = side_len * math.sin(math.radians(base_angle_deg))
        inset = side_len * math.cos(math.radians(base_angle_deg))  # horizontal inset per side
        trap_top = trap_base - 2.0 * inset
        if trap_top <= 0:
            # Fallback: keep a tiny positive top width if parameters are inconsistent
            trap_top = trap_base * 0.1
    
        # Plate is centered at origin; shorter edges are at y = +/- plate_W/2
        y_base = plate_W / 2.0
    
        # Trapezoid vertices (base attached to plate at y=y_base, extending in +Y)
        x0 = x_shift
        p1 = (x0 - trap_base / 2.0, y_base)          # left base
        p2 = (x0 + trap_base / 2.0, y_base)          # right base
        p3 = (x0 + trap_top / 2.0, y_base + h)       # right top
        p4 = (x0 - trap_top / 2.0, y_base + h)       # left top
    
        # --- Build 2D profile and extrude ---
        wp = cq.Workplane("XY")
    
        plate = wp.rect(plate_L, plate_W)
    
        trapezoid = (
            wp.moveTo(*p1)
            .lineTo(*p2)
            .lineTo(*p3)
            .lineTo(*p4)
            .close()
        )
    
        result = (
            wp
            .add(plate)
            .add(trapezoid)
            .extrude(thickness)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00670960/gpt_generated.stl')
