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
        L = 0.75
        W = 0.28043
        H = 0.02045
    
        cut_L = 0.318403
        cut_W = 0.157741
        cut_y_offset = 0.021963  # +Y offset from the midpoint of the base width
    
        # --- Base solid ---
        part = cq.Workplane("XY").box(L, W, H, centered=True)
    
        # --- Cut-out (through all) ---
        part = (
            part.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .center(0, cut_y_offset)
            .rect(cut_L, cut_W)
            .cutThruAll()
        )
    
        # --- Rotate -90 degrees about X axis (around origin) ---
        part = part.rotate((0, 0, 0), (1, 0, 0), -90)
    
        # --- Recenter to origin based on bounding box center ---
        bb = part.val().BoundingBox()
        cx = (bb.xmin + bb.xmax) / 2.0
        cy = (bb.ymin + bb.ymax) / 2.0
        cz = (bb.zmin + bb.zmax) / 2.0
        part = part.translate((-cx, -cy, -cz))
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00002298/gpt_generated.stl')
