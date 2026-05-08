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
        # --- Parameters (units as provided) ---
        top_L = 1.05974
        top_W = 0.362338
        top_H = top_W  # extrude depth equal to width
    
        pocket_L = 0.954546
        pocket_W = 0.261039
        pocket_D = 0.314632
    
        leg_L = 0.041039   # along X (length direction)
        leg_W = 0.136796   # along Y (width direction)
        leg_H = 0.314632   # along Z (height downward from underside)
    
        rod_D = 0.108522
        rod_R = rod_D / 2.0
    
        # Place rod near the bottom of legs (a bit above the very bottom)
        rod_z_from_leg_bottom = rod_R + 0.01  # small clearance
        rod_center_z = -(top_H / 2.0 + leg_H) + rod_z_from_leg_bottom
    
        # Leg centers in X: near left/right ends, centered in Y
        leg_center_x_offset = (top_L / 2.0) - (leg_L / 2.0)
        left_leg_center = (-leg_center_x_offset, 0.0)
        right_leg_center = (leg_center_x_offset, 0.0)
    
        # Rod length equals distance between inner faces of legs (span between legs)
        inner_face_span = (right_leg_center[0] - leg_L / 2.0) - (left_leg_center[0] + leg_L / 2.0)
        rod_length = inner_face_span
    
        # Rod center X is midway between inner faces (which is 0 with symmetric placement)
        rod_center_x = 0.0
    
        # --- Build benchtop ---
        top = cq.Workplane("XY").box(top_L, top_W, top_H, centered=True)
    
        # Hollow pocket from the top face downward
        top = (
            top.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .rect(pocket_L, pocket_W)
            .cutBlind(-pocket_D)
        )
    
        # --- Build legs (as separate solids, then union) ---
        # Legs extend downward from underside of top: center at z = -(top_H/2 + leg_H/2)
        leg_center_z = -(top_H / 2.0 + leg_H / 2.0)
    
        left_leg = (
            cq.Workplane("XY")
            .center(left_leg_center[0], left_leg_center[1])
            .box(leg_L, leg_W, leg_H, centered=True)
            .translate((0, 0, leg_center_z))
        )
    
        right_leg = (
            cq.Workplane("XY")
            .center(right_leg_center[0], right_leg_center[1])
            .box(leg_L, leg_W, leg_H, centered=True)
            .translate((0, 0, leg_center_z))
        )
    
        bench = top.union(left_leg).union(right_leg)
    
        # --- Rod connecting legs near their bottom ends ---
        # Cylinder axis along X (length direction)
        rod = (
            cq.Workplane("YZ", origin=(rod_center_x, 0, rod_center_z))
            .circle(rod_R)
            .extrude(rod_length, both=True)  # symmetric about origin along +X/-X
        )
    
        bench = bench.union(rod)
    
        return bench
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00851553/gpt_generated.stl')
