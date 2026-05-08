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
        table_length = 900.0   # X
        table_width  = 500.0   # Y (also the "extrude amount" for legs per prompt)
        table_thk    = 30.0    # Z thickness of tabletop
    
        leg_height   = table_length / 3.0  # approximately 1/3 of table length
        leg_thk_x    = 60.0                # leg thickness along X
        leg_width_y  = table_width         # same "extrude amount" as table (Y)
    
        # --- Tabletop (centered on XY, sitting above Z=0) ---
        tabletop = (
            cq.Workplane("XY")
            .box(table_length, table_width, table_thk, centered=(True, True, False))
            .translate((0, 0, leg_height))  # lift so legs can sit under it
        )
    
        # --- Legs (two, under left and right sides) ---
        # Place legs so their top touches underside of tabletop at Z=leg_height
        # and their outer faces are flush with the table's left/right edges.
        x_left  = -table_length / 2.0 + leg_thk_x / 2.0
        x_right =  table_length / 2.0 - leg_thk_x / 2.0
        z_leg_center = leg_height / 2.0
    
        leg = cq.Workplane("XY").box(leg_thk_x, leg_width_y, leg_height, centered=(True, True, False))
    
        left_leg = leg.translate((x_left, 0, 0))
        right_leg = leg.translate((x_right, 0, 0))
    
        result = tabletop.union(left_leg).union(right_leg)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00009307/gpt_generated.stl')
