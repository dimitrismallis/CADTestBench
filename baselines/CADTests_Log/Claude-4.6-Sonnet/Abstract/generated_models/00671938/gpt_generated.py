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
        r = 15.0          # radius of each circle
        offset = 10.0     # center offset from origin along X
        height = 20.0     # extrusion height
    
        # --- Step 1: Create first cylinder from circle 1 ---
        cyl1 = (
            cq.Workplane("XY")
            .moveTo(-offset, 0)
            .circle(r)
            .extrude(height)
        )
    
        # --- Step 2: Create second cylinder from circle 2 ---
        cyl2 = (
            cq.Workplane("XY")
            .moveTo(offset, 0)
            .circle(r)
            .extrude(height)
        )
    
        # --- Step 3: Fuse the two solids using Shape-level API ---
        solid1 = cyl1.val()
        solid2 = cyl2.val()
        fused_solid = solid1.fuse(solid2)
    
        # Wrap back into a Workplane
        result = cq.Workplane("XY").add(fused_solid)
    
        # --- Final object verification ---
        TOL = 0.5  # tolerance for checks
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks:
        # X extent: from -(offset + r) to +(offset + r) = -25 to +25 → xlen = 50
        expected_xlen = 2 * (offset + r)  # 50.0
        # Y extent: from -r to +r = -15 to +15 → ylen = 30
        expected_ylen = 2 * r             # 30.0
        # Z extent: 0 to height = 20
        expected_zlen = height            # 20.0
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X bounding box: expected {expected_xlen}, got {bb.xlen}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y bounding box: expected {expected_ylen}, got {bb.ylen}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z bounding box: expected {expected_zlen}, got {bb.zlen}"
    
        # Volume check:
        # Two full circles of radius r, minus the overlapping lens area (counted twice → subtract once)
        # Lens area for two circles of radius r with center distance d=2*offset:
        d = 2 * offset  # 20.0
        # Half-angle subtended: cos(alpha) = d/(2r) = 20/30 = 2/3
        alpha = math.acos(d / (2 * r))
        # Lens area = 2 * r^2 * (alpha - sin(alpha)*cos(alpha))
        lens_area = 2 * r**2 * (alpha - math.sin(alpha) * math.cos(alpha))
        # Union area = 2 * pi * r^2 - lens_area
        union_area = 2 * math.pi * r**2 - lens_area
        expected_volume = union_area * height
    
        actual_volume = solid.Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.02, \
            f"Volume: expected ~{expected_volume:.2f}, got {actual_volume:.2f}"
    
        # Cylindrical faces: OCC splits the fused cylinder surfaces at the intersection seam.
        # Two overlapping cylinders fused together produce 3 cylindrical face segments
        # (one cylinder's arc is split into 2 by the intersection, the other remains 1).
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count >= 2, \
            f"Cylindrical face count: expected >= 2 (got {cyl_face_count})"
    
        # All cylindrical faces should have radius r (within tolerance)
        for i, face in enumerate(result.faces("%Cylinder").vals()):
            face_bb = face.BoundingBox()
            # Each cylindrical face should span the full height
            assert abs(face_bb.zlen - height) < TOL, \
                f"Cylindrical face {i} Z extent: expected {height}, got {face_bb.zlen}"
    
        # Planar faces: top + bottom = at least 2
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count >= 2, \
            f"Planar face count: expected >= 2, got {planar_face_count}"
    
        # Top face(s) should be at max Z = height
        top_bb = result.faces(">Z").val().BoundingBox()
        assert abs(top_bb.zmax - height) < TOL, \
            f"Top face max Z: expected {height}, got {top_bb.zmax}"
    
        # Bottom face(s) should be at min Z = 0
        bot_bb = result.faces("<Z").val().BoundingBox()
        assert abs(bot_bb.zmin - 0) < TOL, \
            f"Bottom face min Z: expected 0, got {bot_bb.zmin}"
    
        # Center of mass should be at (0, 0, height/2) by symmetry
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z - height / 2) < TOL, \
            f"Center of mass Z: expected {height/2}, got {com.z}"
    
        # Containment check: a point inside the overlap region should be inside the solid
        assert solid.isInside((0, 0, height / 2)), \
            "Point (0, 0, 10) should be inside the solid (overlap region)"
    
        # Points outside should NOT be inside
        assert not solid.isInside((offset + r + 1, 0, height / 2)), \
            "Point beyond right edge should be outside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00671938/gpt_generated.stl')
