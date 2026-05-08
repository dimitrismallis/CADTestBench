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
        L = 1.48234
        W = 0.413495
        H = 0.039009
    
        # Right cutout
        r_len = 0.147465
        r_wid = 0.183609
        r_from_right = 0.115044  # distance from right edge to cutout's right edge
    
        # Left cutout
        l_len = 0.320737
        l_wid = 0.187173
        l_from_left = 0.101171   # distance from left edge to cutout's left edge
    
        # Final translation
        dx = 0.008832
        dz = H / 2.0
    
        # --- Compute cutout center positions (base rectangle centered at origin) ---
        x_right_edge = L / 2.0
        x_left_edge = -L / 2.0
    
        # Right cutout: right edge is r_from_right from base right edge
        r_right_edge_x = x_right_edge - r_from_right
        r_center_x = r_right_edge_x - r_len / 2.0
    
        # Left cutout: left edge is l_from_left from base left edge
        l_left_edge_x = x_left_edge + l_from_left
        l_center_x = l_left_edge_x + l_len / 2.0
    
        # --- Build base solid ---
        base = cq.Workplane("XY").rect(L, W).extrude(H)
    
        # --- Cutouts from top face, cut through all (i.e., through thickness H) ---
        result = (
            base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(l_center_x, 0.0).rect(l_len, l_wid)
            .center(r_center_x - l_center_x, 0.0).rect(r_len, r_wid)  # move relative from previous center
            .cutThruAll()
        )
    
        # --- Translate as requested ---
        result = result.translate((dx, 0.0, dz))
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00999126/gpt_generated.stl')
