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
        outer_radius = 20.0
        inner_radius = 16.0
        inner_offset_x = 8.0   # shift inner circle to the right to create crescent
        extrude_depth = 10.0
    
        # --- Step 1: Create the crescent profile using two circles ---
        # Outer circle centered at origin
        outer_circle = cq.Workplane("XY").circle(outer_radius)
    
        # Inner circle offset in X direction (this will be subtracted)
        inner_circle = cq.Workplane("XY").center(inner_offset_x, 0).circle(inner_radius)
    
        # --- Step 2: Extrude both circles and subtract to form crescent ---
        outer_solid = outer_circle.extrude(extrude_depth)
        inner_solid = inner_circle.extrude(extrude_depth)
    
        # Subtract inner from outer to get crescent
        result = outer_solid.cut(inner_solid)
    
        # --- Final object verification ---
        TOL = 0.5  # tolerance for geometric checks
    
        # Compute the intersection X of the two circles analytically:
        # x^2 + y^2 = R^2  (outer, R=20)
        # (x - d)^2 + y^2 = r^2  (inner, d=8, r=16)
        # Subtracting: x^2 - (x-d)^2 = R^2 - r^2
        # 2*d*x - d^2 = R^2 - r^2
        # x = (R^2 - r^2 + d^2) / (2*d)
        d = inner_offset_x
        R = outer_radius
        r = inner_radius
        x_intersect = (R**2 - r**2 + d**2) / (2 * d)
        # x_intersect = (400 - 256 + 64) / 16 = 208/16 = 13.0
    
        # X extent: from -R (leftmost of outer) to x_intersect (where circles meet)
        expected_xlen = x_intersect - (-R)   # = 13 - (-20) = 33
        expected_ylen = 2 * R                # = 40 (outer circle full height)
        expected_zlen = extrude_depth        # = 10
    
        bb = result.val().BoundingBox()
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected ~{expected_xlen}, got {bb.xlen}"
    
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected ~{expected_ylen}, got {bb.ylen}"
    
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Volume check using circle-circle intersection area formula:
        cos_alpha = (d**2 + R**2 - r**2) / (2 * d * R)
        cos_beta  = (d**2 + r**2 - R**2) / (2 * d * r)
        alpha = math.acos(max(-1, min(1, cos_alpha)))
        beta  = math.acos(max(-1, min(1, cos_beta)))
        intersection_area = R**2 * (alpha - math.sin(2*alpha)/2) + r**2 * (beta - math.sin(2*beta)/2)
        crescent_area = math.pi * R**2 - intersection_area
        expected_vol = crescent_area * extrude_depth
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count check:
        # The crescent solid should have:
        # - 1 top flat face (crescent shape)
        # - 1 bottom flat face (crescent shape)
        # - 1 outer cylindrical face (outer arc)
        # - 1 inner cylindrical face (inner arc, the concave side)
        # Total: 4 faces
        face_count = result.faces().size()
        assert face_count == 4, f"Face count: expected 4, got {face_count}"
    
        # Check cylindrical faces (outer arc + inner arc = 2 cylindrical faces)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, f"Cylindrical face count: expected 2, got {cyl_face_count}"
    
        # Check planar faces (top + bottom = 2 planar faces)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 2, f"Planar face count: expected 2, got {planar_face_count}"
    
        # Check that the crescent volume is less than the full outer cylinder
        outer_vol = math.pi * R**2 * extrude_depth
        assert actual_vol < outer_vol, \
            f"Crescent volume should be less than outer cylinder volume ({outer_vol:.2f}), got {actual_vol:.2f}"
    
        # Check center of mass is shifted toward negative X
        # (material is on the left side since inner circle cuts from the right)
        center = cq.Shape.centerOfMass(result.val())
        assert center.x < 0, \
            f"Center of mass X should be negative (crescent opens to right), got {center.x:.3f}"
    
        # Check that a point on the left side of the crescent is inside the solid
        left_point = (-15, 0, extrude_depth / 2)
        assert result.val().isInside(left_point), \
            f"Point {left_point} should be inside the crescent"
    
        # Check that a point in the cut-out region is outside the solid
        # Point at (12, 0, 5): inside inner circle (dist from (8,0) = 4 < 16)
        # and inside outer circle (dist from origin = 12 < 20) → should be cut away
        cutout_point = (12, 0, extrude_depth / 2)
        assert not result.val().isInside(cutout_point), \
            f"Point {cutout_point} should be outside the crescent (in the cut region)"
    
        print(f"✓ Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"✓ Volume: {actual_vol:.2f} (expected ~{expected_vol:.2f})")
        print(f"✓ Faces: {face_count} total, {cyl_face_count} cylindrical, {planar_face_count} planar")
        print(f"✓ Center of mass: ({center.x:.3f}, {center.y:.3f}, {center.z:.3f})")
        print(f"✓ X intersection point: {x_intersect:.2f}, xlen: {expected_xlen:.2f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00673733/gpt_generated.stl')
