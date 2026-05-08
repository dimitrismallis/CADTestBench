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
        sq_size     = 40.0   # square side length
        sq_height   = 8.0    # square extrusion height
        wall_t      = 2.0    # wall thickness for hollowing
        top_floor_t = 2.0    # top floor thickness (top kept solid)
    
        # Center circle (bottom, inside hollow)
        cc_radius  = 4.0
        cc_height  = 6.0    # slightly less than sq_height (8)
    
        # Four corner circles (on top of the square)
        fc_radius  = 3.0    # slightly smaller than cc_radius
        fc_height  = 3.0    # slightly less than sq_height (8)
        fc_offset  = 14.0   # distance from center to each corner circle center
    
        # Box z extents: bottom at z=-4, top at z=+4
        z_bottom = -sq_height / 2   # -4
        z_top    =  sq_height / 2   # +4
    
        # Inner cutout: removes material from bottom, leaving top floor intact
        # Inner cutout height = sq_height - top_floor_t = 6
        # Inner cutout goes from z_bottom to z_bottom + inner_cut_h = -4 to +2
        inner_w         = sq_size - 2 * wall_t    # 36
        inner_cut_h     = sq_height - top_floor_t  # 6
        inner_cut_z_center = z_bottom + inner_cut_h / 2  # -4 + 3 = -1
    
        # --- Step 1: Base square box (40×40×8, centered at origin) ---
        result = cq.Workplane("XY").box(sq_size, sq_size, sq_height)
    
        # --- Step 2: Hollow out inside keeping top intact ---
        # Cut inner box from bottom upward, leaving 2mm top floor
        inner_box = (
            cq.Workplane("XY")
            .box(inner_w, inner_w, inner_cut_h, centered=True)
            .translate((0, 0, inner_cut_z_center))
        )
        result = result.cut(inner_box)
    
        # --- Step 3: Center cylinder from bottom upward (inside hollow) ---
        # Cylinder centered at (0,0), from z_bottom upward cc_height
        cc_z_center = z_bottom + cc_height / 2  # -4 + 3 = -1
        center_cyl = (
            cq.Workplane("XY")
            .cylinder(cc_height, cc_radius)
            .translate((0, 0, cc_z_center))
        )
        result = result.union(center_cyl)
    
        # --- Step 4: Four corner cylinders on top of the square ---
        # Each cylinder sits on top face (z_top = +4), extruded upward fc_height
        fc_z_center = z_top + fc_height / 2  # 4 + 1.5 = 5.5
        corner_positions = [
            ( fc_offset,  fc_offset),
            (-fc_offset,  fc_offset),
            ( fc_offset, -fc_offset),
            (-fc_offset, -fc_offset),
        ]
        for (cx, cy) in corner_positions:
            corner_cyl = (
                cq.Workplane("XY")
                .cylinder(fc_height, fc_radius)
                .translate((cx, cy, fc_z_center))
            )
            result = result.union(corner_cyl)
    
        # --- Final object verification ---
        TOL = 0.1
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks:
        # X and Y: sq_size = 40
        # Z: from z_bottom (-4) to z_top + fc_height (+4+3=+7) → total span = 11
        expected_xlen = sq_size                    # 40
        expected_ylen = sq_size                    # 40
        expected_zlen = sq_height + fc_height      # 8 + 3 = 11
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"BB xlen: expected {expected_xlen}, got {bb.xlen}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"BB ylen: expected {expected_ylen}, got {bb.ylen}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"BB zlen: expected {expected_zlen}, got {bb.zlen}"
    
        # Z extents
        assert abs(bb.zmin - z_bottom) < TOL, \
            f"BB zmin: expected {z_bottom}, got {bb.zmin}"
        assert abs(bb.zmax - (z_top + fc_height)) < TOL, \
            f"BB zmax: expected {z_top + fc_height}, got {bb.zmax}"
    
        # Volume check:
        vol_box   = sq_size * sq_size * sq_height           # 40*40*8 = 12800
        vol_inner = inner_w * inner_w * inner_cut_h         # 36*36*6 = 7776
        vol_cc    = math.pi * cc_radius**2 * cc_height      # π*16*6 ≈ 301.6
        vol_fc    = 4 * math.pi * fc_radius**2 * fc_height  # 4*π*9*3 ≈ 339.3
        expected_vol = vol_box - vol_inner + vol_cc + vol_fc
        actual_vol   = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Cylindrical faces: 1 (center cyl outer) + 4 (corner cyls outer) = 5 minimum
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count >= 5, \
            f"Cylindrical faces: expected >= 5, got {cyl_face_count}"
    
        # Top of square should be solid (not hollow)
        assert solid.isInside((0, 0, z_top - 0.5)), \
            "Point at top floor should be solid"
    
        # Hollow interior: point inside hollow (away from center cyl) should NOT be solid
        hollow_test_pt = (sq_size / 4, sq_size / 4, z_bottom + 1.0)
        assert not solid.isInside(hollow_test_pt), \
            f"Point {hollow_test_pt} should be in hollow region"
    
        # Center cylinder: point at center, above bottom should be solid
        cc_test_pt = (0, 0, z_bottom + 1.0)
        assert solid.isInside(cc_test_pt), \
            f"Point {cc_test_pt} should be inside center cylinder"
    
        # Corner cylinders: point above top face at corner position should be solid
        fc_test_pt = (fc_offset, fc_offset, z_top + 1.0)
        assert solid.isInside(fc_test_pt), \
            f"Point {fc_test_pt} should be inside a corner cylinder"
    
        # Symmetry: center of mass should be near x=0, y=0
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"Center of mass X should be ~0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y should be ~0, got {com.y}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00852000/gpt_generated.stl')
