import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        # Cylinder 1 (top)
        h1 = 0.248985
        d1 = 0.192096
        r1 = d1 / 2  # 0.096048
    
        # Cylinder 2 (middle)
        h2 = 0.220645
        d2 = 0.13302
        r2 = d2 / 2  # 0.06651
    
        # Cylinder 3 (bottom)
        h3 = 0.070261
        d3 = 0.250707
        r3 = d3 / 2  # 0.1253535
    
        # Through-hole
        h_total = h1 + h2 + h3  # 0.539891
        d_hole = 0.098666
        r_hole = d_hole / 2  # 0.049333
    
        # --- Step 1: Build third cylinder (bottom, Z: 0 to h3) ---
        cyl3 = cq.Workplane("XY").cylinder(h3, r3)
        # cylinder() centers by default, so center is at Z=0, spans -h3/2 to +h3/2
        # We need it at Z: 0 to h3, so translate up by h3/2
        cyl3 = cyl3.translate((0, 0, h3 / 2))
    
        # --- Step 2: Build second cylinder (middle, Z: h3 to h3+h2) ---
        cyl2 = cq.Workplane("XY").cylinder(h2, r2)
        # Center at Z = h3 + h2/2
        cyl2 = cyl2.translate((0, 0, h3 + h2 / 2))
    
        # --- Step 3: Build first cylinder (top, Z: h3+h2 to h3+h2+h1) ---
        cyl1 = cq.Workplane("XY").cylinder(h1, r1)
        # Center at Z = h3 + h2 + h1/2
        cyl1 = cyl1.translate((0, 0, h3 + h2 + h1 / 2))
    
        # --- Step 4: Union all three cylinders ---
        result = cyl3.union(cyl2).union(cyl1)
    
        # --- Step 5: Cut the central through-hole ---
        hole = cq.Workplane("XY").cylinder(h_total, r_hole)
        hole = hole.translate((0, 0, h_total / 2))
        result = result.cut(hole)
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Check bounding box
        bb = result.val().BoundingBox()
    
        # X and Y extents: dominated by the widest cylinder (cyl3, d3=0.250707)
        assert abs(bb.xlen - d3) < TOL, f"X extent: expected {d3}, got {bb.xlen}"
        assert abs(bb.ylen - d3) < TOL, f"Y extent: expected {d3}, got {bb.ylen}"
    
        # Z extent: total height
        assert abs(bb.zlen - h_total) < TOL, f"Z extent: expected {h_total}, got {bb.zlen}"
    
        # Z min should be 0, Z max should be h_total
        assert abs(bb.zmin - 0.0) < TOL, f"Z min: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - h_total) < TOL, f"Z max: expected {h_total}, got {bb.zmax}"
    
        # Volume check:
        # Vol = pi*r3^2*h3 + pi*r2^2*h2 + pi*r1^2*h1 - pi*r_hole^2*h_total
        vol_cyl3 = math.pi * r3**2 * h3
        vol_cyl2 = math.pi * r2**2 * h2
        vol_cyl1 = math.pi * r1**2 * h1
        vol_hole = math.pi * r_hole**2 * h_total
        expected_vol = vol_cyl3 + vol_cyl2 + vol_cyl1 - vol_hole
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical faces exist (the three outer cylinders + the inner hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 4, f"Expected at least 4 cylindrical faces, got {cyl_faces}"
    
        # Check the through-hole: a line along Z through center should intersect faces
        shape = result.val()
        # Point inside the hole region (center, mid-height)
        mid_z = h_total / 2
        # The hole center is at (0,0), check that a point just inside hole radius is NOT inside solid
        # (since it's been cut out)
        point_in_hole = (0.0, 0.0, mid_z)
        assert not shape.isInside(point_in_hole), \
            f"Center point should be inside the hole (not solid), but isInside returned True"
    
        # A point at r2 (middle cylinder radius) at mid-height of cyl2 should be inside solid
        mid_cyl2_z = h3 + h2 / 2
        point_in_cyl2 = (r2 * 0.8, 0.0, mid_cyl2_z)
        assert shape.isInside(point_in_cyl2), \
            f"Point inside cyl2 should be inside solid, but isInside returned False"
    
        # Check center of mass is approximately on Z axis
        com = cq.Shape.centerOfMass(shape)
        assert abs(com.x) < TOL, f"Center of mass X should be ~0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y should be ~0, got {com.y}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00003763/gpt_generated.stl')
