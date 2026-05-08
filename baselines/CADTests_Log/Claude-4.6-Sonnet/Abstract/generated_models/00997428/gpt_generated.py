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
        outer_radius = 30.0
        height = 60.0
        inner_radius = 27.0
        cavity_depth = 55.0       # hole depth, less than height → solid bottom remains
        wall_thickness = outer_radius - inner_radius  # 3 mm
    
        rod_radius = 3.0
        rod_length = 2 * outer_radius + 10.0  # 70 mm, slightly larger than diameter (60 mm)
        rod_z = height - 8.0                  # near the top, at z=52
    
        # --- Step 1: Outer cylinder (bucket body) ---
        bucket = (
            cq.Workplane("XY")
            .circle(outer_radius)
            .extrude(height)
        )
    
        # --- Step 2: Inner hollow (cavity) — cut from top, not all the way through ---
        bucket = (
            bucket
            .faces(">Z")
            .workplane()
            .circle(inner_radius)
            .cutBlind(cavity_depth)
        )
    
        # --- Step 3: Horizontal cylindrical rod passing through both sides near the top ---
        # Build rod as a standalone solid on the YZ plane, extruding along X
        # Origin at (-rod_length/2, 0, rod_z) so rod spans x: -35 to +35
        rod = (
            cq.Workplane("YZ", origin=(-rod_length / 2, 0, rod_z))
            .circle(rod_radius)
            .extrude(rod_length)
        )
    
        # Get the underlying Shape objects and perform boolean union at shape level
        bucket_solid = bucket.val()
        rod_solid = rod.val()
    
        # Fuse the two solids together
        fused = bucket_solid.fuse(rod_solid)
    
        # Wrap back into a Workplane
        result = cq.Workplane("XY").add(fused)
    
        # --- Final object verification ---
        TOL = 0.5  # generous tolerance for curved surfaces
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        expected_x = rod_length        # 70 mm (rod extends ±35 mm)
        expected_y = 2 * outer_radius  # 60 mm (cylinder diameter)
        expected_z = height            # 60 mm
    
        assert abs(bb.xlen - expected_x) < TOL, \
            f"X extent: expected {expected_x}, got {bb.xlen}"
        assert abs(bb.ylen - expected_y) < TOL, \
            f"Y extent: expected {expected_y}, got {bb.ylen}"
        assert abs(bb.zlen - expected_z) < TOL, \
            f"Z extent: expected {expected_z}, got {bb.zlen}"
    
        # Z range: bottom at 0, top at height
        assert abs(bb.zmin) < TOL, f"Z min: expected ~0, got {bb.zmin}"
        assert abs(bb.zmax - height) < TOL, f"Z max: expected {height}, got {bb.zmax}"
    
        # X range: rod centered at x=0
        assert abs(bb.xmin - (-rod_length / 2)) < TOL, \
            f"X min: expected {-rod_length/2}, got {bb.xmin}"
        assert abs(bb.xmax - (rod_length / 2)) < TOL, \
            f"X max: expected {rod_length/2}, got {bb.xmax}"
    
        # Volume check:
        vol_outer = math.pi * outer_radius**2 * height
        vol_cavity = math.pi * inner_radius**2 * cavity_depth
        vol_rod = math.pi * rod_radius**2 * rod_length
        vol_bucket_only = vol_outer - vol_cavity
        # Upper bound: bucket + full rod (rod partially overlaps cylinder walls)
        vol_upper_bound = vol_bucket_only + vol_rod
    
        actual_vol = result.val().Volume()
    
        assert actual_vol > vol_bucket_only * 0.95, \
            f"Volume too small: {actual_vol:.1f} < {vol_bucket_only * 0.95:.1f}"
        assert actual_vol < vol_upper_bound * 1.05, \
            f"Volume too large: {actual_vol:.1f} > {vol_upper_bound * 1.05:.1f}"
    
        # Cylindrical faces: outer cylinder, inner cavity, rod curved face
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 3, f"Expected at least 3 cylindrical faces, got {cyl_faces}"
    
        # Check cavity: a point inside the hollow should NOT be inside the solid
        cavity_test_point = (0, 0, 30)  # z=30, well inside the hollow
        assert not result.val().isInside(cavity_test_point), \
            f"Point {cavity_test_point} should be in the hollow cavity, not inside solid"
    
        # Check solid bottom: z from 0 to (height - cavity_depth) = 5 mm
        bottom_solid_point = (0, 0, 2.5)  # z=2.5, inside the 5mm solid bottom
        assert result.val().isInside(bottom_solid_point), \
            f"Point {bottom_solid_point} should be inside the solid bottom"
    
        # Check rod extends outside cylinder on +X side
        rod_outside_point = (outer_radius + 2, 0, rod_z)
        assert result.val().isInside(rod_outside_point), \
            f"Point {rod_outside_point} should be inside the rod (outside cylinder, +X)"
    
        # Check rod extends outside cylinder on -X side
        rod_outside_neg = (-outer_radius - 2, 0, rod_z)
        assert result.val().isInside(rod_outside_neg), \
            f"Point {rod_outside_neg} should be inside the rod (outside cylinder, -X)"
    
        # Check rod is near the top — point in cylinder wall at rod height
        rod_wall_point = (outer_radius - wall_thickness / 2, 0, rod_z)
        assert result.val().isInside(rod_wall_point), \
            f"Point {rod_wall_point} should be inside the cylinder wall at rod height"
    
        print(f"All assertions passed!")
        print(f"Bounding box: X={bb.xlen:.2f}, Y={bb.ylen:.2f}, Z={bb.zlen:.2f}")
        print(f"Volume: {actual_vol:.2f} mm³")
        print(f"Cylindrical faces: {cyl_faces}")
        print(f"vol_bucket_only={vol_bucket_only:.1f}, vol_upper_bound={vol_upper_bound:.1f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00997428/gpt_generated.stl')
