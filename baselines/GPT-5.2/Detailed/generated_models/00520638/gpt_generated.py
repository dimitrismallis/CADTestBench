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
        length = 1.10769
        width = 0.474725
        height = 0.18989
    
        cyl_d = 0.5 * length
        cyl_r = cyl_d / 2.0
        cyl_h = width
    
        conn_xy = cyl_d
        conn_h = cyl_h / 2.0
    
        inner_d = 0.194358
        inner_r = inner_d / 2.0
        slot_w = inner_d
        slot_h = inner_d
    
        # --- Base box (centered at origin) ---
        base = cq.Workplane("XY").box(length, width, height, centered=True)
    
        # --- Main cylinder on top, shifted so it partially protrudes from base ---
        cyl_shift_x = (length / 2.0) - (0.65 * cyl_r)  # protrude beyond +X
        z_base_top = height / 2.0
    
        # Create cylinder from z=0..cyl_h then move it so its bottom sits on base top
        main_cyl = (
            cq.Workplane("XY")
            .center(cyl_shift_x, 0)
            .circle(cyl_r)
            .extrude(cyl_h)  # along +Z
            .translate((0, 0, z_base_top))
        )
    
        # --- Connector box centered on top of cylinder ---
        conn_center_z = z_base_top + cyl_h + conn_h / 2.0
        connector = (
            cq.Workplane("XY")
            .box(conn_xy, conn_xy, conn_h, centered=True)
            .translate((cyl_shift_x, 0, conn_center_z))
        )
    
        part = base.union(main_cyl).union(connector)
    
        # --- Subtractive inner cylinder (through cylinder+connector) ---
        cut_cyl_h = cyl_h + conn_h + height + 0.5
        # Make it start below base top and extend upward enough to clear connector
        inner_cyl_cut = (
            cq.Workplane("XY")
            .center(cyl_shift_x, 0)
            .circle(inner_r)
            .extrude(cut_cyl_h)
            .translate((0, 0, z_base_top - 0.25))  # start slightly below base top
        )
    
        # --- Subtractive inner box (slot) through center of cylinder+connector) ---
        inner_box_cut = (
            cq.Workplane("XY")
            .box(slot_w, slot_h, cut_cyl_h, centered=True)
            .translate((cyl_shift_x, 0, z_base_top + cut_cyl_h / 2.0 - 0.25))
        )
    
        part = part.cut(inner_cyl_cut).cut(inner_box_cut)
    
        # --- Arm: polyline in XY, extruded along width of base (Y direction) ---
        arm_pts = [
            (0.0, 0.316484),
            (-0.056, 0.483119),
            (length / 2.0, 0.613244),
            (length / 2.0, 0.434708),
        ]
    
        arm_profile = (
            cq.Workplane("XY")
            .moveTo(*arm_pts[0])
            .lineTo(*arm_pts[1])
            .lineTo(*arm_pts[2])
            .lineTo(*arm_pts[3])
            .close()
        )
    
        # Extrude along +Z then rotate so extrusion becomes +Y.
        arm_thickness = width
        arm = arm_profile.extrude(arm_thickness)  # along +Z
        arm = arm.translate((0, 0, -arm_thickness / 2.0))  # center it about Z=0
        arm = arm.rotate((0, 0, 0), (1, 0, 0), 90)  # Z -> Y
    
        # Place arm roughly at top of base
        arm = arm.translate((0, 0, z_base_top))
    
        part = part.union(arm)
    
        # --- Final alignment transform (rotate + translate) ---
        part = part.rotate((0, 0, 0), (0, 0, 1), 90)
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00520638/gpt_generated.stl')
