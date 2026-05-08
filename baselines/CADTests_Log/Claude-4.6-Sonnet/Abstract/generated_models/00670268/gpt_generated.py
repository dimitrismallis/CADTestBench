import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        # Cylinder 1 (large, long)
        c1_diameter = 80.0
        c1_radius   = c1_diameter / 2       # 40
        c1_height   = 100.0
    
        # Cylinder 2 (small, on top face, slightly below center)
        c2_height   = c1_height / 8         # 12.5
        c2_diameter = c1_diameter / 4       # 20
        c2_radius   = c2_diameter / 2       # 10
        c2_offset_y = -10.0                 # "slightly below center" in -Y
    
        # Cylinder 3 (concentric with c2, on top of c2)
        c3_height   = c2_height * 2         # 25
        c3_diameter = c2_diameter / 2       # 10
        c3_radius   = c3_diameter / 2       # 5
    
        # --- Derived positions ---
        c1_z_top  = c1_height / 2           # 50  (top of cyl1)
        c2_z_base = c1_z_top                # 50  (cyl2 starts at top of cyl1)
        c2_z_top  = c2_z_base + c2_height   # 62.5
        c3_z_base = c2_z_top                # 62.5 (cyl3 starts at top of cyl2)
        c3_z_top  = c3_z_base + c3_height   # 87.5
    
        # Center Z values (for containment checks)
        c2_center_z = c2_z_base + c2_height / 2   # 56.25
        c3_center_z = c3_z_base + c3_height / 2   # 75.0
    
        # --- Step 1: Large main cylinder (centered at origin) ---
        # Extends from z = -50 to z = +50
        cyl1 = cq.Workplane("XY").cylinder(c1_height, c1_radius)
    
        # --- Step 2: Second cylinder protruding from top face, slightly below center ---
        # Place workplane at the BASE of cyl2 (z = c2_z_base = 50), extrude upward
        cyl2 = (
            cq.Workplane("XY")
            .workplane(offset=c2_z_base)
            .center(0, c2_offset_y)
            .circle(c2_radius)
            .extrude(c2_height)
        )
    
        # --- Step 3: Third cylinder concentric with c2, on top of c2 ---
        # Place workplane at the BASE of cyl3 (z = c3_z_base = 62.5), extrude upward
        cyl3 = (
            cq.Workplane("XY")
            .workplane(offset=c3_z_base)
            .center(0, c2_offset_y)
            .circle(c3_radius)
            .extrude(c3_height)
        )
    
        # --- Step 4: Union all three cylinders ---
        result = cyl1.union(cyl2).union(cyl3)
    
        # --- Final object verification ---
        TOL = 0.1
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # X extent: dominated by cyl1 diameter = 80
        assert abs(bb.xlen - c1_diameter) < TOL, \
            f"X extent: expected {c1_diameter}, got {bb.xlen}"
    
        # Y extent: cyl1 goes from -40 to +40 → ylen = 80
        assert abs(bb.ylen - c1_diameter) < TOL, \
            f"Y extent: expected {c1_diameter}, got {bb.ylen}"
    
        # Z extent: from -50 (bottom of cyl1) to 87.5 (top of cyl3) = 137.5
        expected_zlen = c1_height / 2 + c3_z_top
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z extent: expected {expected_zlen}, got {bb.zlen}"
    
        # Z min/max
        assert abs(bb.zmin - (-c1_height / 2)) < TOL, \
            f"Z min: expected {-c1_height/2}, got {bb.zmin}"
        assert abs(bb.zmax - c3_z_top) < TOL, \
            f"Z max: expected {c3_z_top}, got {bb.zmax}"
    
        # Volume check
        vol_c1 = math.pi * c1_radius**2 * c1_height
        vol_c2 = math.pi * c2_radius**2 * c2_height
        vol_c3 = math.pi * c3_radius**2 * c3_height
        # cyl2 and cyl3 protrude above cyl1 — no overlap with cyl1
        # cyl3 protrudes above cyl2 — no overlap with cyl2
        expected_vol = vol_c1 + vol_c2 + vol_c3
        actual_vol   = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Cylindrical face count: 3 cylinders → 3 curved faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 3, \
            f"Cylindrical faces: expected 3, got {cyl_faces}"
    
        # Check that cyl2 center point is inside the solid
        c2_mid = (0, c2_offset_y, c2_center_z)
        assert solid.isInside(c2_mid), \
            f"Point {c2_mid} should be inside the solid (inside cyl2)"
    
        # Check that cyl3 center point is inside the solid
        c3_mid = (0, c2_offset_y, c3_center_z)
        assert solid.isInside(c3_mid), \
            f"Point {c3_mid} should be inside the solid (inside cyl3)"
    
        # Check that a point well above cyl3 is NOT inside
        outside_pt = (0, 0, c3_z_top + 5)
        assert not solid.isInside(outside_pt), \
            f"Point {outside_pt} should be outside the solid"
    
        # Verify cyl3 is concentric with cyl2 (same XY center), check a point just above cyl2 top
        c3_check = (0, c2_offset_y, c3_z_base + 1)
        assert solid.isInside(c3_check), \
            f"Point {c3_check} should be inside cyl3"
    
        # Verify cyl2 is offset from cyl1's axis:
        # At cyl2 height, a point at (0, +5, c2_center_z) should be outside
        # (distance from cyl2 center (0,-10) to (0,5) = 15 > c2_radius=10)
        outside_c2 = (0, 5, c2_center_z)
        assert not solid.isInside(outside_c2), \
            f"Point {outside_c2} should be outside cyl2 (and above cyl1)"
    
        print("All assertions passed!")
        print(f"  Cyl1: diameter={c1_diameter}, height={c1_height}")
        print(f"  Cyl2: diameter={c2_diameter}, height={c2_height}, offset_y={c2_offset_y}")
        print(f"  Cyl3: diameter={c3_diameter}, height={c3_height}, concentric with cyl2")
        print(f"  Bounding box: x={bb.xlen:.2f}, y={bb.ylen:.2f}, z={bb.zlen:.2f}")
        print(f"  Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00670268/gpt_generated.stl')
