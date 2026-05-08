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
        outer_d = 60.0
        height = 70.0
    
        inner_d = 50.0
        cavity_depth = 60.0  # smaller than height so it doesn't go all the way through
    
        rod_d = 6.0
        rod_len = outer_d + 10.0  # slightly larger than bucket diameter
        rod_z = height - 12.0     # towards the top
    
        # --- Bucket body (outer cylinder) ---
        bucket = cq.Workplane("XY").circle(outer_d / 2).extrude(height)
    
        # --- Hollow cavity (blind cut from the top) ---
        bucket = (
            bucket
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .circle(inner_d / 2)
            .cutBlind(-cavity_depth)  # negative goes downward from the top face
        )
    
        # --- Horizontal rod passing through both sides near the top ---
        # Create on YZ plane so extrusion goes along X.
        rod_half = (
            cq.Workplane("YZ", origin=(0, 0, rod_z))
            .circle(rod_d / 2)
            .extrude(rod_len / 2)  # extrude in +X
        )
        rod = rod_half.union(rod_half.mirror("YZ"))  # mirror to -X to make it centered
    
        final_result = bucket.union(rod)
        return final_result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00997428/gpt_generated.stl')
