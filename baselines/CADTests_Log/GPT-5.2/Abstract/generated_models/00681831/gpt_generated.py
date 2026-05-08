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
        r = 25.0
        height = 20.0
    
        # Isosceles trapezium cutout parameters
        trap_top_w = 10.0
        trap_bot_w = 16.0
        trap_depth = 8.0
    
        y_top = r
        y_bot = r - trap_depth
    
        pts = [
            (-trap_top_w / 2.0, y_top),
            ( trap_top_w / 2.0, y_top),
            ( trap_bot_w / 2.0, y_bot),
            (-trap_bot_w / 2.0, y_bot),
        ]
    
        # Outer wire: circle
        outer_wire = cq.Workplane("XY").circle(r).wire().val()
    
        # Inner wire: trapezoid (the cutout)
        inner_wire = (
            cq.Workplane("XY")
            .moveTo(*pts[0])
            .lineTo(*pts[1])
            .lineTo(*pts[2])
            .lineTo(*pts[3])
            .close()
            .wire()
            .val()
        )
    
        # Make a face with a hole (inner wire) and extrude it
        face = cq.Face.makeFromWires(outer_wire, [inner_wire])
        result = cq.Workplane("XY").add(face).extrude(height)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00681831/gpt_generated.stl')
