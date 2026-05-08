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
        height = 20.0          # extrusion height (Z)
        top_w = 40.0           # top width of outer trapezoid
        bottom_w = 70.0        # bottom width of outer trapezoid
        trap_h = 35.0          # trapezoid height in sketch (Y direction)
        wall = 5.0             # wall thickness around the hole
    
        # Inner trapezoid dimensions (smaller than outer)
        inner_top_w = top_w - 2 * wall
        inner_bottom_w = bottom_w - 2 * wall
        inner_trap_h = trap_h - 2 * wall
    
        if inner_top_w <= 0 or inner_bottom_w <= 0 or inner_trap_h <= 0:
            raise ValueError("Wall thickness too large for given trapezoid dimensions.")
    
        def sketch_trapezoid(wp: cq.Workplane, top_width: float, bottom_width: float, h: float) -> cq.Workplane:
            """Create a centered trapezoid as pending wire(s) on the given workplane."""
            y_top = h / 2.0
            y_bot = -h / 2.0
            x_t = top_width / 2.0
            x_b = bottom_width / 2.0
    
            return (
                wp.moveTo(-x_b, y_bot)
                  .lineTo(x_b, y_bot)
                  .lineTo(x_t, y_top)
                  .lineTo(-x_t, y_top)
                  .close()
            )
    
        # --- Outer solid ---
        outer = sketch_trapezoid(cq.Workplane("XY"), top_w, bottom_w, trap_h).extrude(height)
    
        # --- Inner trapezoid hole cut through all ---
        top_wp = outer.faces(">Z").workplane(centerOption="CenterOfMass")
        result = sketch_trapezoid(top_wp, inner_top_w, inner_bottom_w, inner_trap_h).cutThruAll()
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00985482/gpt_generated.stl')
