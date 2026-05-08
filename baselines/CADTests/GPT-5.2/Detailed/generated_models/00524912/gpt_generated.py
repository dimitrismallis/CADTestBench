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
        L1 = 0.416808  # large length (X)
        W1 = 0.033235  # large width  (Y)
        H1 = 0.75      # large height (Z)
    
        L2 = 0.211685  # small length (along Y, in YZ plane)
        W2 = 0.065736  # small width  (along Z, in YZ plane)
        H2 = 0.411987  # small thickness/extrude (along X)
        pad = 0.0065309
    
        # --- Large rectangle (door) in XY plane, extruded along Z ---
        door = cq.Workplane("XY").box(L1, W1, H1, centered=True)
    
        # --- Small rectangle (hinge) in YZ plane, extruded along X ---
        # Create with dimensions: thickness along X = H2, length along Y = L2, width along Z = W2
        hinge = cq.Workplane("XY").box(H2, L2, W2, centered=True)
    
        # Position hinge:
        # 1) Centered at same XY as door (already at origin in Y)
        # 2) Connect at one edge to door: place hinge so its -X face is at door's +X face
        x_shift = (L1 / 2.0) + (H2 / 2.0)
        # 3) Padding from base (bottom) of door: hinge bottom at door bottom + pad
        # door bottom z = -H1/2; hinge bottom z = z_center - W2/2
        z_center = (-H1 / 2.0) + pad + (W2 / 2.0)
    
        hinge = hinge.translate((x_shift, 0.0, z_center))
    
        # Union into final part
        result = door.union(hinge)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00524912/gpt_generated.stl')
