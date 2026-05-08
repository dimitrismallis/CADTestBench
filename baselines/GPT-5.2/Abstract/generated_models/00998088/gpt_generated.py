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
        plate_len = 120.0   # X
        plate_wid = 40.0    # Y
        plate_thk = 4.0     # Z
    
        cut_sq = 14.0       # square cutout size
        cut_rad = 2.0       # corner radius
        edge_margin = 3.0   # inset from outer edges
    
        # --- Base plate ---
        plate = cq.Workplane("XY").rect(plate_len, plate_wid).extrude(plate_thk)
    
        # Cutout centers at two corners along the +Y long edge
        x_off = plate_len / 2 - edge_margin - cut_sq / 2
        y_off = plate_wid / 2 - edge_margin - cut_sq / 2
    
        # Rounded square sketch (2D fillet done in Sketch API)
        rounded_square = cq.Sketch().rect(cut_sq, cut_sq).vertices().fillet(cut_rad)
    
        # Place two sketches and cut through
        result = (
            plate
            .faces(">Z").workplane()
            .placeSketch(
                rounded_square.moved(cq.Location(cq.Vector( x_off, y_off, 0))),
                rounded_square.moved(cq.Location(cq.Vector(-x_off, y_off, 0))),
            )
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00998088/gpt_generated.stl')
