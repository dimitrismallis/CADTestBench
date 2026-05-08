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
        L = 1.48234       # length (X)
        W = 0.413495      # width (Y)
        H = 0.039009      # height (Z)
    
        # Right cutout
        rc_len = 0.147465   # X dimension
        rc_wid = 0.183609   # Y dimension (cuts from one Y edge)
        rc_off = 0.115044   # distance from right X edge to near side of cutout
    
        # Left cutout
        lc_len = 0.320737   # X dimension
        lc_wid = 0.187173   # Y dimension
        lc_off = 0.101171   # distance from left X edge to near side of cutout
    
        # Translation
        tx = 0.008832
        tz = H / 2.0  # translate half height upward to center vertically (from -H/2..H/2 → 0..H)
    
        # --- Step 1: Compute cutout centers ---
        # Right cutout: near X edge at (L/2 - rc_off), far X edge at (L/2 - rc_off - rc_len)
        #   cuts from +Y edge downward by rc_wid
        rc_cx = L/2 - rc_off - rc_len/2   # X center
        rc_cy = W/2 - rc_wid/2            # Y center (from +Y edge)
    
        # Left cutout: near X edge at (-L/2 + lc_off), far X edge at (-L/2 + lc_off + lc_len)
        #   cuts from -Y edge upward by lc_wid
        lc_cx = -L/2 + lc_off + lc_len/2  # X center
        lc_cy = -W/2 + lc_wid/2           # Y center (from -Y edge)
    
        # --- Step 2: Create base rectangle extruded symmetrically about XY plane ---
        # Using both=True extrudes from -H/2 to +H/2 (centered at Z=0)
        result = (
            cq.Workplane("XY")
            .rect(L, W)
            .extrude(H/2, both=True)
        )
    
        # Subtract right cutout (symmetric extrusion)
        right_cutout = (
            cq.Workplane("XY")
            .center(rc_cx, rc_cy)
            .rect(rc_len, rc_wid)
            .extrude(H/2, both=True)
        )
    
        # Subtract left cutout (symmetric extrusion)
        left_cutout = (
            cq.Workplane("XY")
            .center(lc_cx, lc_cy)
            .rect(lc_len, lc_wid)
            .extrude(H/2, both=True)
        )
    
        result = result.cut(right_cutout).cut(left_cutout)
    
        # --- Step 3: Translate: +tx in X, +tz in Z (centers vertically: -H/2..H/2 → 0..H) ---
        result = result.translate((tx, 0, tz))
    
        # --- Final object verification ---
        TOL = 1e-4
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        expected_xmin = -L/2 + tx
        expected_xmax =  L/2 + tx
        expected_ymin = -W/2
        expected_ymax =  W/2
        expected_zmin = 0.0
        expected_zmax = H
    
        assert abs(bb.xmin - expected_xmin) < TOL, f"xmin: expected {expected_xmin:.6f}, got {bb.xmin:.6f}"
        assert abs(bb.xmax - expected_xmax) < TOL, f"xmax: expected {expected_xmax:.6f}, got {bb.xmax:.6f}"
        assert abs(bb.ymin - expected_ymin) < TOL, f"ymin: expected {expected_ymin:.6f}, got {bb.ymin:.6f}"
        assert abs(bb.ymax - expected_ymax) < TOL, f"ymax: expected {expected_ymax:.6f}, got {bb.ymax:.6f}"
        assert abs(bb.zmin - expected_zmin) < TOL, f"zmin: expected {expected_zmin:.6f}, got {bb.zmin:.6f}"
        assert abs(bb.zmax - expected_zmax) < TOL, f"zmax: expected {expected_zmax:.6f}, got {bb.zmax:.6f}"
    
        assert abs(bb.xlen - L) < TOL, f"xlen: expected {L}, got {bb.xlen}"
        assert abs(bb.ylen - W) < TOL, f"ylen: expected {W}, got {bb.ylen}"
        assert abs(bb.zlen - H) < TOL, f"zlen: expected {H}, got {bb.zlen}"
    
        # Volume check: base - right cutout - left cutout
        base_vol = L * W * H
        rc_vol = rc_len * rc_wid * H
        lc_vol = lc_len * lc_wid * H
        expected_vol = base_vol - rc_vol - lc_vol
    
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check Z center (should be at H/2 after translation)
        center = solid.Center()
        assert abs(center.z - H/2) < TOL, f"Z center: expected {H/2:.6f}, got {center.z:.6f}"
    
        # Check that cutouts exist by verifying faces count > 6
        face_count = result.faces().size()
        assert face_count > 6, f"Face count should be > 6 (cutouts add faces), got {face_count}"
    
        # Verify right cutout region is empty (point inside cutout should be outside solid)
        rc_world_x = rc_cx + tx
        rc_world_y = rc_cy
        rc_world_z = H / 2
        assert not solid.isInside((rc_world_x, rc_world_y, rc_world_z)), \
            f"Right cutout region should be empty at ({rc_world_x:.4f}, {rc_world_y:.4f}, {rc_world_z:.4f})"
    
        # Verify left cutout region is empty
        lc_world_x = lc_cx + tx
        lc_world_y = lc_cy
        lc_world_z = H / 2
        assert not solid.isInside((lc_world_x, lc_world_y, lc_world_z)), \
            f"Left cutout region should be empty at ({lc_world_x:.4f}, {lc_world_y:.4f}, {lc_world_z:.4f})"
    
        # Verify center of rectangle is solid (not cut out)
        assert solid.isInside((tx, 0, H/2)), \
            f"Center of rectangle should be solid at ({tx:.4f}, 0, {H/2:.4f})"
    
        print(f"All assertions passed!")
        print(f"Bounding box: X=[{bb.xmin:.5f}, {bb.xmax:.5f}], Y=[{bb.ymin:.5f}, {bb.ymax:.5f}], Z=[{bb.zmin:.5f}, {bb.zmax:.5f}]")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Face count: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00999126/gpt_generated.stl')
