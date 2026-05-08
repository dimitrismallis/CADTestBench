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
        table_L = 1.5
        table_W = 0.32143
        table_H = 0.064286
    
        leg_L = 0.064286
        leg_W = 0.32143
        leg_H = 0.47129
    
        # Leg placement: ~1/3 of table length from each end
        # End-to-leg-center distance = (table_L/2 - table_L/3) = table_L/6
        x_offset = table_L / 6.0
    
        # --- Tabletop: top surface at Z=0, thickness downward ---
        top = cq.Workplane("XY").box(table_L, table_W, table_H, centered=(True, True, False))
    
        # --- Legs: positioned under the tabletop, centered in Y ---
        # Place legs so their top meets the underside of the tabletop (at Z = -table_H)
        leg_z = -table_H - leg_H / 2.0
    
        left_leg = (
            cq.Workplane("XY")
            .box(leg_L, leg_W, leg_H, centered=True)
            .translate((-x_offset, 0, leg_z))
        )
    
        right_leg = (
            cq.Workplane("XY")
            .box(leg_L, leg_W, leg_H, centered=True)
            .translate((x_offset, 0, leg_z))
        )
    
        desk = top.union(left_leg).union(right_leg)
        return desk
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00009307/gpt_generated.stl')
