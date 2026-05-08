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
        # Given dimensions (units as provided)
        rect_len = 0.051687   # along X (short edge)
        rect_wid = 0.120604   # along Y (long edge)
        height = 0.75         # extrusion height along Z
    
        # Trapezium (isosceles) parameters
        trap_base = rect_len          # attached to rectangle short edge
        trap_top = rect_len * 0.6     # chosen smaller top base (not specified)
        trap_h = rect_wid * 0.5       # chosen trapezium height (not specified)
    
        # Rectangle centered at origin
        rect = cq.Workplane("XY").rect(rect_len, rect_wid)
    
        # Trapezium attached to the rectangle's +Y short edge:
        # Rectangle spans y in [-rect_wid/2, +rect_wid/2]
        y0 = rect_wid / 2.0           # attachment line (base) at +Y edge of rectangle
        y1 = y0 + trap_h              # top of trapezium
    
        # Isosceles trapezoid points (counter-clockwise)
        p1 = (-trap_base/2.0, y0)
        p2 = ( trap_base/2.0, y0)
        p3 = ( trap_top/2.0,  y1)
        p4 = (-trap_top/2.0,  y1)
    
        trap = (
            cq.Workplane("XY")
            .moveTo(*p1).lineTo(*p2).lineTo(*p3).lineTo(*p4).close()
        )
    
        # Combine the two 2D regions and extrude
        profile = rect.add(trap)
        result = profile.extrude(height)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00670457/gpt_generated.stl')
