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
        inch = 25.4
    
        # --- Parameters (inches) ---
        plate_xy = 1.3125
        plate_thk = 0.0625
    
        hole_d = 0.05
        # "near a corner" -> place holes inset from edges
        hole_inset = 0.10  # inches from each edge
    
        cyl_od = 1.0
        cyl_id = 0.9375
        cyl_h = 0.6875
    
        z_shift = 0.03125
    
        # --- Convert to mm ---
        plate_xy_mm = plate_xy * inch
        plate_thk_mm = plate_thk * inch
    
        hole_d_mm = hole_d * inch
        hole_inset_mm = hole_inset * inch
    
        cyl_od_mm = cyl_od * inch
        cyl_id_mm = cyl_id * inch
        cyl_h_mm = cyl_h * inch
    
        z_shift_mm = z_shift * inch
    
        # --- Base plate with corner holes ---
        # Use a construction rectangle sized so its vertices are inset from the plate edges.
        hole_rect = plate_xy_mm - 2.0 * hole_inset_mm
    
        plate = (
            cq.Workplane("XY")
            .rect(plate_xy_mm, plate_xy_mm)
            .extrude(plate_thk_mm)
            .faces(">Z").workplane()
            .rect(hole_rect, hole_rect, forConstruction=True)
            .vertices()
            .hole(hole_d_mm)
        )
    
        # --- Hollow cylinder (ring), centered, extruded so it intersects/extends through plate ---
        ring = (
            cq.Workplane("XY")
            .circle(cyl_od_mm / 2.0)
            .circle(cyl_id_mm / 2.0)
            .extrude(cyl_h_mm)
        )
    
        # Union and translate in Z
        asm = plate.union(ring).translate((0, 0, z_shift_mm))
        return asm
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00983173/gpt_generated.stl')
