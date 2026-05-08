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
        rect_len = 120.0   # long dimension of rectangle (X)
        rect_w   = 30.0    # short dimension of rectangle (Y) -> trapezium base length
        trap_h   = 25.0    # trapezium height (extends in +X from rectangle short edge)
        trap_top = 16.0    # trapezium top base length (must be < rect_w for isosceles)
        thickness = 12.0   # extrusion height (Z)
    
        if trap_top >= rect_w:
            raise ValueError("trap_top must be smaller than rect_w to form an isosceles trapezium.")
    
        # Rectangle corners (centered at origin)
        xL, xR = -rect_len / 2.0, rect_len / 2.0
        yB, yT = -rect_w / 2.0, rect_w / 2.0
    
        # Trapezium attached to the rectangle's +X short edge at x = xR
        # Base is the rectangle short edge: from (xR, yB) to (xR, yT)
        # Top base is centered and shorter, at x = xR + trap_h
        y_top_half = trap_top / 2.0
        xTbase = xR + trap_h
    
        pts = [
            (xL, yB),          # rectangle bottom-left
            (xR, yB),          # rectangle bottom-right (start of trapezium base)
            (xTbase, -y_top_half),  # trapezium top-right (slanted side)
            (xTbase,  y_top_half),  # trapezium top-left
            (xR, yT),          # rectangle top-right (end of trapezium base)
            (xL, yT),          # rectangle top-left
        ]
    
        profile = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
        )
    
        result = profile.extrude(thickness)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00670457/gpt_generated.stl')
