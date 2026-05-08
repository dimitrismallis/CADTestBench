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
        base_L = 1.5
        base_W = 1.2
        base_H = 0.147638
    
        pocket_L = 0.975
        pocket_W = 0.675
        pocket_depth = 0.11811
    
        plate2_L = 1.25274
        plate2_W = 0.982742
        plate2_H = 0.041339
    
        boss_L = 0.059055
        boss_W = 0.11811
        boss_H = 0.088583
    
        # Distances of boss from the end/side edges of the 2nd rectangle
        dist_from_end = 0.390573   # from length end
        dist_from_side = 0.314204  # from width side
    
        # Convert edge distances to boss center offsets from plate2 center
        # Plate2 spans x in [-L/2, +L/2], y in [-W/2, +W/2]
        x_center = (plate2_L / 2.0) - dist_from_end - (boss_L / 2.0)
        y_center = (plate2_W / 2.0) - dist_from_side - (boss_W / 2.0)
    
        # --- Base with centered pocket ---
        base = (
            cq.Workplane("XY")
            .box(base_L, base_W, base_H, centered=(True, True, False))  # bottom at Z=0
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(pocket_L, pocket_W)
            .cutBlind(-pocket_depth)
        )
    
        # --- Second rectangle on top of base ---
        plate2 = (
            cq.Workplane("XY", origin=(0, 0, base_H))
            .box(plate2_L, plate2_W, plate2_H, centered=(True, True, False))
        )
    
        # --- Two bosses on top of second rectangle (mirrored) ---
        bosses = (
            cq.Workplane("XY", origin=(0, 0, base_H + plate2_H))
            .pushPoints([(x_center, y_center), (x_center, -y_center)])
            .rect(boss_L, boss_W)
            .extrude(boss_H)
        )
    
        asm = base.union(plate2).union(bosses)
    
        # --- Translate so base is centered vertically at its half height (base centered about Z=0) ---
        asm = asm.translate((0, 0, -base_H / 2.0))
    
        return asm
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00522865/gpt_generated.stl')
