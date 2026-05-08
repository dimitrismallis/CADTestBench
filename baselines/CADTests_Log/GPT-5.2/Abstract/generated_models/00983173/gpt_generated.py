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
        plate_size = 60.0
        plate_thk = 4.0
    
        hole_d = 2.0
        corner_margin = 6.0  # distance from each edge to hole center
    
        tube_od = 24.0
        tube_id = 16.0
        tube_h = 30.0  # tall enough to extend through the plate
    
        # --- Base plate (centered about origin) ---
        plate = cq.Workplane("XY").box(plate_size, plate_size, plate_thk, centered=True)
    
        # --- Four corner holes (through the plate) ---
        pts = [
            ( plate_size / 2 - corner_margin,  plate_size / 2 - corner_margin),
            (-plate_size / 2 + corner_margin,  plate_size / 2 - corner_margin),
            (-plate_size / 2 + corner_margin, -plate_size / 2 + corner_margin),
            ( plate_size / 2 - corner_margin, -plate_size / 2 + corner_margin),
        ]
        plate = plate.faces(">Z").workplane().pushPoints(pts).hole(hole_d)
    
        # --- Hollow cylinder (tube), centered on origin, extending through plate ---
        tube = (
            cq.Workplane("XY")
            .circle(tube_od / 2)
            .circle(tube_id / 2)
            .extrude(tube_h)                 # extrudes in +Z from Z=0
            .translate((0, 0, -tube_h / 2))  # center it about Z=0
        )
    
        # Union so the tube intersects the plate in the middle
        result = plate.union(tube)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00983173/gpt_generated.stl')
