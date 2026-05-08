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
        # Parameters
        square_size = 100.0          # central square side length (X and Y)
        height = 20.0                # extrusion height magnitude
        side_width = square_size / 5 # ~1/5 of square width
    
        # Central square extruded +Z from the XY plane (base at Z=0)
        core = cq.Workplane("XY").rect(square_size, square_size).extrude(height)
    
        # Two side rectangles (same Y length as square), attached left and right,
        # extruded in the opposite direction (-Z) by the same magnitude.
        # Place them so they are flush with the core's left/right sides.
        left = (
            cq.Workplane("XY")
            .center(-(square_size / 2 + side_width / 2), 0)
            .rect(side_width, square_size)
            .extrude(-height)
        )
    
        right = (
            cq.Workplane("XY")
            .center((square_size / 2 + side_width / 2), 0)
            .rect(side_width, square_size)
            .extrude(-height)
        )
    
        result = core.union(left).union(right)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00520130/gpt_generated.stl')
