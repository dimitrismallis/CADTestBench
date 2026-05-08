import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        base_l = 1.5
        base_w = 1.2
        base_h = 0.147638
    
        hollow_l = 0.975
        hollow_w = 0.675
        hollow_d = 0.11811
    
        rect2_l = 1.25274
        rect2_w = 0.982742
        rect2_h = 0.041339
    
        rect3_l = 0.059055
        rect3_w = 0.11811
        rect3_h = 0.088583
    
        dist_from_end  = 0.390573
        dist_from_side = 0.314204
    
        # Post x/y positions relative to center
        post_x = rect2_l / 2 - dist_from_end   # 0.235797
        post_y = rect2_w / 2 - dist_from_side  # 0.177167
    
        # Z centers (before final translation, base centered at z=0)
        base_z_center  = 0.0
        rect2_z_center = base_h / 2 + rect2_h / 2
        post_z_center  = base_h / 2 + rect2_h + rect3_h / 2
    
        # --- Step 1: Build base solid ---
        base_solid = cq.Workplane("XY").box(base_l, base_w, base_h).val()
    
        # --- Step 2: Build hollow cutter ---
        # Hollow is cut from top of base downward by hollow_d
        # Hollow center z = base_h/2 - hollow_d/2
        hollow_z_center = base_h / 2 - hollow_d / 2
        hollow_cutter = (
            cq.Workplane(cq.Plane(origin=(0, 0, hollow_z_center), normal=(0, 0, 1)))
            .box(hollow_l, hollow_w, hollow_d)
            .val()
        )
    
        # --- Step 3: Build rect2 solid ---
        rect2_solid = (
            cq.Workplane(cq.Plane(origin=(0, 0, rect2_z_center), normal=(0, 0, 1)))
            .box(rect2_l, rect2_w, rect2_h)
            .val()
        )
    
        # --- Step 4: Build post1 solid ---
        post1_solid = (
            cq.Workplane(cq.Plane(origin=(post_x, post_y, post_z_center), normal=(0, 0, 1)))
            .box(rect3_l, rect3_w, rect3_h)
            .val()
        )
    
        # --- Step 5: Build post2 solid (mirrored) ---
        post2_solid = (
            cq.Workplane(cq.Plane(origin=(-post_x, post_y, post_z_center), normal=(0, 0, 1)))
            .box(rect3_l, rect3_w, rect3_h)
            .val()
        )
    
        # --- Step 6: Combine all solids using Shape boolean operations ---
        # Union base + rect2 + post1 + post2, then subtract hollow
        combined = base_solid.fuse(rect2_solid).fuse(post1_solid).fuse(post2_solid)
        combined = combined.cut(hollow_cutter)
    
        # --- Step 7: Translate so base bottom is at z=0 ---
        combined = combined.translate(cq.Vector(0, 0, base_h / 2))
    
        # Wrap in Workplane for return
        result = cq.Workplane("XY").add(combined)
    
        # --- Final object verification ---
        TOL = 1e-3
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - base_l) < TOL, \
            f"X length: expected {base_l}, got {bb.xlen}"
        assert abs(bb.ylen - base_w) < TOL, \
            f"Y length: expected {base_w}, got {bb.ylen}"
    
        expected_zmin = 0.0
        expected_zmax = base_h + rect2_h + rect3_h
        expected_zlen = expected_zmax
        assert abs(bb.zmin - expected_zmin) < TOL, \
            f"Z min: expected {expected_zmin}, got {bb.zmin}"
        assert abs(bb.zmax - expected_zmax) < TOL, \
            f"Z max: expected {expected_zmax}, got {bb.zmax}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Volume check
        base_vol   = base_l * base_w * base_h
        hollow_vol = hollow_l * hollow_w * hollow_d
        rect2_vol  = rect2_l * rect2_w * rect2_h
        rect3_vol  = rect3_l * rect3_w * rect3_h
        expected_vol = base_vol - hollow_vol + rect2_vol + 2 * rect3_vol
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check hollow exists: center of hollow should be outside solid
        # After translation: hollow occupies z from (base_h - hollow_d) to base_h
        # hollow center z = base_h - hollow_d/2
        hollow_center_z = base_h - hollow_d / 2
        hollow_test_pt = (0.0, 0.0, hollow_center_z)
        assert not solid.isInside(hollow_test_pt, tolerance=1e-4), \
            f"Hollow: point {hollow_test_pt} should be outside (in hollow)"
    
        # Check base rim is solid (corner of base, away from hollow)
        base_rim_pt = (base_l/2 - 0.05, base_w/2 - 0.05, base_h * 0.5)
        assert solid.isInside(base_rim_pt, tolerance=1e-4), \
            f"Base rim: point {base_rim_pt} should be inside solid"
    
        # Check posts exist
        post_center_z = base_h + rect2_h + rect3_h / 2
        assert solid.isInside((post_x, post_y, post_center_z), tolerance=1e-4), \
            f"Post 1: should be inside solid"
        assert solid.isInside((-post_x, post_y, post_center_z), tolerance=1e-4), \
            f"Post 2: should be inside solid"
    
        # Check rect2 exists
        rect2_mid_z = base_h + rect2_h / 2
        assert solid.isInside((0.0, 0.0, rect2_mid_z), tolerance=1e-4), \
            f"Rect2: center point should be inside solid"
    
        print("All assertions passed!")
        print(f"Bounding box: {bb.xlen:.6f} x {bb.ylen:.6f} x {bb.zlen:.6f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00522865/gpt_generated.stl')
