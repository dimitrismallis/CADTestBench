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
        outer_radius = 50.0
        inner_radius = 35.0
        height = 40.0
        cap_thickness = 3.0
    
        # --- Step 1: Create the annulus (ring) profile and extrude it ---
        # Draw outer circle, then subtract inner circle to form annulus, then extrude
        annulus = (
            cq.Workplane("XY")
            .circle(outer_radius)       # outer circle
            .circle(inner_radius)       # inner circle (creates a hole in the profile)
            .extrude(height)            # extrude upward to form hollow cylinder
        )
    
        # --- Step 2: Create a filled circle (disk) at the bottom to close it ---
        # The bottom cap sits at Z=0 (bottom of the annulus), thickness goes downward
        # We place it so it aligns with the bottom of the annulus
        bottom_cap = (
            cq.Workplane("XY")
            .circle(outer_radius)       # solid disk with outer radius
            .extrude(cap_thickness)     # thin disk (cap_thickness upward)
        )
    
        # --- Step 3: Union the annulus with the bottom cap ---
        result = annulus.union(bottom_cap)
    
        # --- Final object verification ---
        TOL = 0.5  # tolerance for volume/area checks
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        # X and Y span: from -outer_radius to +outer_radius
        assert abs(bb.xlen - 2 * outer_radius) < TOL, \
            f"X length: expected {2*outer_radius}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * outer_radius) < TOL, \
            f"Y length: expected {2*outer_radius}, got {bb.ylen}"
        # Z span: from 0 to height (cap is absorbed into annulus base since both start at Z=0)
        assert abs(bb.zlen - height) < TOL, \
            f"Z length: expected {height}, got {bb.zlen}"
        assert abs(bb.zmin) < TOL, \
            f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - height) < TOL, \
            f"Z max: expected {height}, got {bb.zmax}"
    
        # Volume check:
        # Annulus volume = pi * (R_outer^2 - R_inner^2) * height
        # Bottom cap volume = pi * R_outer^2 * cap_thickness
        # But the cap overlaps with the annulus for the ring portion (0 to cap_thickness)
        # Union volume = annulus_vol + cap_vol - overlap
        # overlap = annulus ring portion at cap_thickness = pi*(R_outer^2 - R_inner^2)*cap_thickness
        # So total = pi*(R_outer^2 - R_inner^2)*height + pi*R_outer^2*cap_thickness - pi*(R_outer^2 - R_inner^2)*cap_thickness
        #          = pi*(R_outer^2 - R_inner^2)*height + pi*R_inner^2*cap_thickness
        annulus_vol = math.pi * (outer_radius**2 - inner_radius**2) * height
        cap_vol = math.pi * outer_radius**2 * cap_thickness
        overlap_vol = math.pi * (outer_radius**2 - inner_radius**2) * cap_thickness
        expected_vol = annulus_vol + cap_vol - overlap_vol
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Face count checks:
        # The final shape should have:
        # - 1 outer cylindrical face (full height)
        # - 1 inner cylindrical face (full height, the bore)
        # - 1 top annular face (ring at top)
        # - 1 bottom flat circular face (the cap bottom)
        # - 1 inner cap face (annular ring at cap_thickness height, where cap meets bore)
        # Total: 5 faces
        face_count = result.faces().size()
        assert face_count == 5, \
            f"Face count: expected 5, got {face_count}"
    
        # Check cylindrical faces (outer wall + inner bore = 2 cylindrical faces)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, \
            f"Cylindrical face count: expected 2, got {cyl_face_count}"
    
        # Check planar faces (top annulus + bottom disk + inner ledge = 3 planar faces)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 3, \
            f"Planar face count: expected 3, got {planar_face_count}"
    
        # Check the top face is at Z = height
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - height) < TOL, \
            f"Top face Z center: expected {height}, got {top_face_z}"
    
        # Check the bottom face is at Z = 0
        bot_face_z = result.faces("<Z").val().Center().z
        assert abs(bot_face_z) < TOL, \
            f"Bottom face Z center: expected 0, got {bot_face_z}"
    
        # Check center of mass is on the Z axis (symmetry)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
    
        # Check the inner bore: a point inside the bore should NOT be inside the solid
        # (e.g., at mid-height, at radius = (inner_radius/2))
        bore_point = (0, inner_radius / 2, height / 2)
        assert not solid.isInside(bore_point), \
            f"Point {bore_point} should be outside (in the bore), but isInside returned True"
    
        # Check a point inside the wall IS inside the solid
        wall_mid_radius = (outer_radius + inner_radius) / 2
        wall_point = (wall_mid_radius, 0, height / 2)
        assert solid.isInside(wall_point), \
            f"Point {wall_point} should be inside the wall, but isInside returned False"
    
        # Check a point inside the cap IS inside the solid
        cap_point = (0, 0, cap_thickness / 2)
        assert solid.isInside(cap_point), \
            f"Point {cap_point} should be inside the cap, but isInside returned False"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"  Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
        print(f"  Faces: {face_count} total ({cyl_face_count} cylindrical, {planar_face_count} planar)")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00520675/gpt_generated.stl')
