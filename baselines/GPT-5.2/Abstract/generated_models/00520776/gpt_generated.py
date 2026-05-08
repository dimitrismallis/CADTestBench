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
        # Parameters (mm)
        outer_radius = 10.0
        height = 20.0
        tiny_hole_radius = 0.5  # very small hole
    
        # Outer cylinder (positive extrusion)
        part = (
            cq.Workplane("XY")
            .circle(outer_radius)
            .extrude(height)
        )
    
        # Tiny hole (negative extrusion / cut)
        part = (
            part
            .faces(">Z")
            .workplane()
            .circle(tiny_hole_radius)
            .cutThruAll()
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00520776/gpt_generated.stl')
