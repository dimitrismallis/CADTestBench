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
        outer_radius = 30.0
        wall_thickness = 3.0
        height = 60.0
    
        bottom_thickness = 3.0
    
        tiny_hole_diameter = 4.0  # "tiny hollow circle" (a small hole)
        tiny_hole_depth = bottom_thickness  # through the bottom cap only
    
        inner_radius = outer_radius - wall_thickness
    
        # --- Large hollow cylinder (tube) ---
        tube = (
            cq.Workplane("XY")
            .circle(outer_radius)
            .circle(inner_radius)
            .extrude(height)
        )
    
        # --- Bottom circle to close it (a disk/cap) ---
        bottom_cap = (
            cq.Workplane("XY")
            .circle(outer_radius)
            .extrude(bottom_thickness)
        )
    
        # Combine tube + cap
        result = tube.union(bottom_cap)
    
        # --- Tiny hollow circle in the middle of the circle (cut a small hole in the cap) ---
        result = (
            result
            .faces("<Z")                 # bottom face of the cap
            .workplane(centerOption="CenterOfMass")
            .hole(tiny_hole_diameter, depth=tiny_hole_depth)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00522355/gpt_generated.stl')
