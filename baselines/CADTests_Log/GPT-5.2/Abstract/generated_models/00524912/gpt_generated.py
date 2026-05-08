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
        big_len_x = 100.0   # X size of large rectangle
        big_wid_y = 60.0    # Y size of large rectangle
        big_thk   = 4.0     # thickness of large plate (along Z)
    
        # Smaller rectangle ~ half length and width (relative to big plate in-plane dims)
        small_len_y = big_wid_y * 0.5   # along Y (in YZ plane)
        small_wid_z = big_len_x * 0.5   # along Z (in YZ plane)
        small_thk   = big_thk * 1.9     # almost twice the big thickness (along X)
    
        # Large plate: sketch on XY, extrude +Z, then shift down by half thickness to center on Z=0
        big_plate = (
            cq.Workplane("XY")
            .rect(big_len_x, big_wid_y)
            .extrude(big_thk)
            .translate((0, 0, -big_thk / 2.0))
        )
    
        # Small plate: sketch on YZ, extrude +X, then shift back by half thickness to center on X=0
        small_plate = (
            cq.Workplane("YZ")
            .rect(small_len_y, small_wid_z)  # dimensions in (Y, Z)
            .extrude(small_thk)
            .translate((-small_thk / 2.0, 0, 0))
        )
    
        # Union to connect them (hinge-like perpendicular plates)
        final_result = big_plate.union(small_plate)
    
        return final_result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00524912/gpt_generated.stl')
