import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        L = 1.5          # main rectangle length (X)
        W = 0.413793     # main rectangle width (Y)
        H = 0.031034     # extrusion height (Z)
    
        cut_L = (L - 1.28276) / 2   # = 0.10862
        cut_W = W - 0.31034          # = 0.103453
        fillet_r = 0.025
    
        # --- Step 1: Create main rectangular plate ---
        # box() is centered at origin by default: Z spans from -H/2 to +H/2
        result = cq.Workplane("XY").box(L, W, H)
    
        # --- Step 2: Define cutout profiles with fillets on inner corners ---
        # Left cutout corners (in world XY):
        # Outer (left) edge: x = -L/2  (no fillet, flush with plate edge)
        # Inner (right) edge: x = -L/2 + cut_L  (fillet on these two corners)
        # Bottom: y = -cut_W/2,  Top: y = +cut_W/2
    
        r = fillet_r
        x_outer_L = -L/2
        x_inner_L = -L/2 + cut_L
        y_bot = -cut_W / 2
        y_top = +cut_W / 2
    
        cos45 = math.cos(math.radians(45))
        sin45 = math.sin(math.radians(45))
    
        # Bottom-right inner corner arc midpoint (center at x_inner_L, y_bot):
        # Arc from (x_inner_L - r, y_bot) [angle=180°] to (x_inner_L, y_bot + r) [angle=90°]
        # Midpoint at angle=135°: center + r*(cos135, sin135)
        arc_bot_mid_x = x_inner_L - r * cos45
        arc_bot_mid_y = y_bot + r * sin45
    
        # Top-right inner corner arc midpoint (center at x_inner_L, y_top):
        # Arc from (x_inner_L, y_top - r) [angle=270°] to (x_inner_L - r, y_top) [angle=180°]
        # Midpoint at angle=225°: center + r*(cos225, sin225)
        arc_top_mid_x = x_inner_L - r * cos45
        arc_top_mid_y = y_top - r * sin45
    
        # Extrude height: start below box bottom, extend above box top to ensure full cut
        extrude_start_z = -H / 2 - 0.01
        extrude_height = H + 0.02
    
        # Left cutout profile (counterclockwise winding):
        left_cut_wire = (
            cq.Workplane(cq.Plane(origin=(0, 0, extrude_start_z), normal=(0, 0, 1)))
            .moveTo(x_outer_L, y_bot)
            .lineTo(x_inner_L - r, y_bot)
            .threePointArc(
                (arc_bot_mid_x, arc_bot_mid_y),
                (x_inner_L, y_bot + r)
            )
            .lineTo(x_inner_L, y_top - r)
            .threePointArc(
                (arc_top_mid_x, arc_top_mid_y),
                (x_inner_L - r, y_top)
            )
            .lineTo(x_outer_L, y_top)
            .close()
        )
    
        # Right cutout (mirror): inner corners on LEFT side (x = L/2 - cut_L)
        x_outer_R = L/2
        x_inner_R = L/2 - cut_L
    
        # Bottom-left inner corner arc midpoint (center at x_inner_R, y_bot):
        # Arc from (x_inner_R + r, y_bot) [angle=0°] to (x_inner_R, y_bot + r) [angle=90°]
        # Midpoint at angle=45°: center + r*(cos45, sin45)
        arc_bot_mid_x_R = x_inner_R + r * cos45
        arc_bot_mid_y_R = y_bot + r * sin45
    
        # Top-left inner corner arc midpoint (center at x_inner_R, y_top):
        # Arc from (x_inner_R, y_top - r) [angle=270°] to (x_inner_R + r, y_top) [angle=0°]
        # Midpoint at angle=315°: center + r*(cos315, sin315) = center + r*(cos45, -sin45)
        arc_top_mid_x_R = x_inner_R + r * cos45
        arc_top_mid_y_R = y_top - r * sin45
    
        right_cut_wire = (
            cq.Workplane(cq.Plane(origin=(0, 0, extrude_start_z), normal=(0, 0, 1)))
            .moveTo(x_outer_R, y_bot)
            .lineTo(x_inner_R + r, y_bot)
            .threePointArc(
                (arc_bot_mid_x_R, arc_bot_mid_y_R),
                (x_inner_R, y_bot + r)
            )
            .lineTo(x_inner_R, y_top - r)
            .threePointArc(
                (arc_top_mid_x_R, arc_top_mid_y_R),
                (x_inner_R + r, y_top)
            )
            .lineTo(x_outer_R, y_top)
            .close()
        )
    
        # --- Step 3: Extrude cut solids and subtract from main plate ---
        left_cut_solid = left_cut_wire.extrude(extrude_height)
        right_cut_solid = right_cut_wire.extrude(extrude_height)
    
        result = result.cut(left_cut_solid)
        result = result.cut(right_cut_solid)
    
        # --- Final object verification ---
        TOL = 0.001
    
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - L) < TOL, f"X length: expected {L}, got {bb.xlen}"
        assert abs(bb.ylen - W) < TOL, f"Y width: expected {W}, got {bb.ylen}"
        assert abs(bb.zlen - H) < TOL, f"Z height: expected {H}, got {bb.zlen}"
    
        # Volume check: main box minus two cutouts (with fillet correction)
        main_vol = L * W * H
        cutout_rect_area = cut_L * cut_W
        # Each cutout has 2 filleted corners: fillet reduces cutout area by (r^2 - pi*r^2/4) per corner
        corner_area_removed = r**2 - math.pi * r**2 / 4
        cutout_area = cutout_rect_area - 2 * corner_area_removed
        expected_vol = main_vol - 2 * cutout_area * H
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check symmetry: center of mass should be at (0, 0, 0)
        # box() is centered at origin, so CoM Z = 0 (spans -H/2 to +H/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X not centered: {com.x}"
        assert abs(com.y) < TOL, f"CoM Y not centered: {com.y}"
        assert abs(com.z) < TOL, f"CoM Z: expected 0.0 (box centered at origin), got {com.z}"
    
        # Check that cutout regions are empty (not inside solid)
        # Sample point well inside each cutout region (away from fillet zones)
        left_cut_center = (-L/2 + cut_L * 0.3, 0.0, 0.0)
        assert not result.val().isInside(left_cut_center), \
            f"Left cutout region should be empty but point {left_cut_center} is inside solid"
    
        right_cut_center = (L/2 - cut_L * 0.3, 0.0, 0.0)
        assert not result.val().isInside(right_cut_center), \
            f"Right cutout region should be empty but point {right_cut_center} is inside solid"
    
        # Check that center of plate is solid
        center_point = (0.0, 0.0, 0.0)
        assert result.val().isInside(center_point), \
            f"Center of plate should be solid but point {center_point} is not inside"
    
        # Check cylindrical faces exist (from fillets) - 2 cutouts x 2 fillets = 4 cylindrical faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 4, f"Expected 4 cylindrical faces from fillets, got {cyl_faces}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00998088/gpt_generated.stl')
