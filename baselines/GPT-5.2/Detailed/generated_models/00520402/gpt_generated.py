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
        height = 0.75
        od = 0.078575
        id_ = 0.058318
    
        cut_d = 0.078654
    
        ro = od / 2.0
        ri = id_ / 2.0
        cut_r = cut_d / 2.0
    
        # --- Base tube (hollow cylinder) ---
        tube = (
            cq.Workplane("XY")
            .circle(ro)
            .circle(ri)
            .extrude(height)
            .translate((0, 0, -height / 2.0))  # center about Z=0
        )
    
        # --- Semi-circular cutter profile on YZ plane ---
        # Build a half-disk (semicircle + diameter) as a closed wire, then extrude along X.
        cutter_len = od * 3.0  # long enough to pass through tube
    
        # Semicircle in YZ plane: endpoints at (y=-r,z=0) and (y=+r,z=0), bulging to +Z via mid point (0,+r)
        cutter = (
            cq.Workplane("YZ")
            .moveTo(-cut_r, 0)
            .threePointArc((0, cut_r), (cut_r, 0))  # arc through +Z side
            .lineTo(-cut_r, 0)                      # diameter line
            .close()
            .extrude(cutter_len, both=True)         # extrude along +/-X
        )
    
        # Rotate/position the cutter to achieve desired orientation and bite into the tube wall
        open_angle_deg = 90  # rotate about X axis
        bite = ro * 0.6      # push into tube (tunable)
    
        cutter = (
            cutter
            .rotate((0, 0, 0), (1, 0, 0), open_angle_deg)
            .translate((0, bite, 0))
        )
    
        result = tube.cut(cutter)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00520402/gpt_generated.stl')
