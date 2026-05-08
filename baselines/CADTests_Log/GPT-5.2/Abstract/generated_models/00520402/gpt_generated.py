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
        outer_d = 40.0
        wall = 3.0
        inner_d = outer_d - 2 * wall
        length = 160.0
    
        # Semi-circular cut (a half-cylinder notch)
        notch_r = outer_d * 0.35          # radius of the semi-circular cut
        notch_len = outer_d * 1.2         # length of the cut along X (through the tube)
        notch_z_center = 0.0              # centered vertically through the tube
    
        # --- Base: long hollow cylinder (tube) ---
        tube = (
            cq.Workplane("XY")
            .circle(outer_d / 2)
            .circle(inner_d / 2)
            .extrude(length, both=True)   # long tube centered at Z=0, extends along +Z/-Z
        )
    
        # --- Cut: semi-circular shape in the middle of the cylinder ---
        # Create a half-cylinder oriented along X, then position it at the tube mid-length (Z=0).
        # Profile is a semicircle in the YZ plane, extruded along X.
        half_cyl_cut = (
            cq.Workplane("YZ")
            .moveTo(0, 0)
            .radiusArc((0, 2 * notch_r), notch_r)  # semicircle from (0,0) to (0,2R)
            .close()
            .extrude(notch_len, both=True)         # extrude along X
            .translate((0, 0, notch_z_center))
        )
    
        result = tube.cut(half_cyl_cut)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00520402/gpt_generated.stl')
