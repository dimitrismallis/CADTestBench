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
        outer_dia = 0.503822
        outer_rad = outer_dia / 2.0          # 0.251911
        outer_height = 0.75
    
        inner_dia = 0.426316
        inner_rad = inner_dia / 2.0          # 0.213158
        inner_depth = 0.710526               # cut depth from top
    
        rod_dia = 0.05921
        rod_rad = rod_dia / 2.0              # 0.029605
        rod_length = 0.631579
        top_margin = 0.049342
        rod_z = outer_height - top_margin    # 0.700658 (center of rod)
    
        # --- Step 1: Outer cylinder (base at Z=0, top at Z=outer_height) ---
        bucket = (
            cq.Workplane("XY")
            .circle(outer_rad)
            .extrude(outer_height)
        )
    
        # --- Step 2: Hollow interior - cut from top downward using explicit solid ---
        # Build the inner hollow cylinder explicitly and subtract it
        # Inner cylinder: base at Z = outer_height - inner_depth, top at Z = outer_height
        inner_cyl = (
            cq.Workplane("XY")
            .workplane(offset=outer_height - inner_depth)
            .circle(inner_rad)
            .extrude(inner_depth)
        )
        bucket = bucket.cut(inner_cyl)
    
        # --- Step 3: Horizontal rod passing through both sides ---
        # Rod is along X axis, centered at (0, 0, rod_z)
        # Build rod: circle on YZ plane at origin=(0,0,rod_z), extrude along +X and -X
        rod_full = (
            cq.Workplane(
                cq.Plane(
                    origin=(-rod_length / 2.0, 0, rod_z),
                    xDir=(0, 1, 0),
                    normal=(1, 0, 0)
                )
            )
            .circle(rod_rad)
            .extrude(rod_length)
        )
    
        # --- Step 4: Union bucket and rod ---
        result = bucket.union(rod_full)
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # Bounding box X: rod extends from -rod_length/2 to +rod_length/2
        expected_xlen = rod_length  # 0.631579 (rod is wider than cylinder)
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected ~{expected_xlen:.4f}, got {bb.xlen:.4f}"
    
        # Bounding box Y: cylinder dominates Y extent = outer_dia
        expected_ylen = outer_dia  # 0.503822
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected ~{expected_ylen:.4f}, got {bb.ylen:.4f}"
    
        # Bounding box Z: 0 to outer_height = 0.75
        expected_zlen = outer_height  # 0.75
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected ~{expected_zlen:.4f}, got {bb.zlen:.4f}"
    
        # Volume check:
        vol_outer = math.pi * outer_rad**2 * outer_height
        vol_inner = math.pi * inner_rad**2 * inner_depth
        vol_rod = math.pi * rod_rad**2 * rod_length
    
        vol_bucket = vol_outer - vol_inner  # ~0.04815
        # Rod overlap with bucket walls: rod passes through the cylinder walls
        # The overlap is approximately the rod cross-section times the chord through the annular wall
        # For a conservative check: actual volume should be between vol_bucket and vol_bucket + vol_rod
        expected_vol_min = vol_bucket * 0.85
        expected_vol_max = vol_bucket + vol_rod * 1.1
    
        actual_vol = result.val().Volume()
        assert actual_vol > expected_vol_min, \
            f"Volume too small: expected > {expected_vol_min:.5f}, got {actual_vol:.5f}"
        assert actual_vol < expected_vol_max, \
            f"Volume too large: expected < {expected_vol_max:.5f}, got {actual_vol:.5f}"
    
        # Check cylindrical faces exist (outer cylinder, inner hollow, rod)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 3, \
            f"Expected at least 3 cylindrical faces, got {cyl_faces}"
    
        # Check the hollow: a point inside the hollow should NOT be inside the solid
        # Hollow occupies from Z = outer_height - inner_depth to Z = outer_height
        # i.e., from Z = 0.039474 to Z = 0.75, radius < inner_rad
        hollow_center_z = outer_height - inner_depth / 2.0  # ~0.394737
        hollow_test_point = (0, 0, hollow_center_z)
        solid_shape = result.val()
        assert not solid_shape.isInside(hollow_test_point), \
            f"Point {hollow_test_point} should be inside the hollow (not solid), but isInside returned True"
    
        # Check the bottom is solid: a point near the bottom center should be inside
        # Bottom solid thickness = outer_height - inner_depth = 0.039474
        bottom_test_z = (outer_height - inner_depth) / 2.0  # ~0.019737
        bottom_test_point = (0, 0, bottom_test_z)
        assert solid_shape.isInside(bottom_test_point), \
            f"Point {bottom_test_point} should be inside the solid bottom, but isInside returned False"
    
        # Check rod extends beyond cylinder on both sides
        assert bb.xmin < -outer_rad - TOL, \
            f"Rod should extend beyond cylinder in -X: xmin={bb.xmin:.4f}, outer_rad={outer_rad:.4f}"
        assert bb.xmax > outer_rad + TOL, \
            f"Rod should extend beyond cylinder in +X: xmax={bb.xmax:.4f}, outer_rad={outer_rad:.4f}"
    
        # Check rod Z position: rod top should be near rod_z + rod_rad
        rod_top = rod_z + rod_rad
        # The overall Z max is outer_height (cylinder top), rod_top < outer_height
        assert bb.zmax >= outer_height - TOL, \
            f"Z max should reach outer_height: expected ~{outer_height}, got {bb.zmax:.4f}"
    
        # Verify the rod is present at the correct height by checking a point on the rod
        # outside the cylinder boundary
        rod_test_point = (rod_length / 2.0 - 0.01, 0, rod_z)
        assert solid_shape.isInside(rod_test_point), \
            f"Point on rod {rod_test_point} should be inside solid, but isInside returned False"
    
        print(f"All assertions passed!")
        print(f"Bounding box: X={bb.xlen:.4f}, Y={bb.ylen:.4f}, Z={bb.zlen:.4f}")
        print(f"Volume: {actual_vol:.6f}")
        print(f"Cylindrical faces: {cyl_faces}")
        print(f"vol_bucket={vol_bucket:.5f}, vol_rod={vol_rod:.5f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00997428/gpt_generated.stl')
