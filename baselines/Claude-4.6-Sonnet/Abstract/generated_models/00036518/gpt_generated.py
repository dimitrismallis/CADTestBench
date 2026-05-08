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
        r = 10.0          # radius
        d = 2 * r         # diameter = 20
        h = 2 * d         # height = 40 (height = 2 * diameter)
    
        # --- Step 1: Create the base cylinder ---
        # Centered at origin, axis along Z
        cylinder = cq.Workplane("XY").cylinder(h, r)
    
        # --- Step 2: Define the angled cutting plane ---
        # We want to remove exactly 1/3 of the cylinder volume.
        # Volume of cylinder = π * r² * h
        # For a tilted plane cutting through the cylinder:
        # If the plane passes through (x=+r, z=z1) and (x=-r, z=z2),
        # the volume BELOW the plane = π * r² * (z1 + z2) / 2
        # (This is exact for a linear tilt across the diameter)
        #
        # Cylinder spans z = -h/2 to z = +h/2 (centered at origin)
        # We want to remove the UPPER portion (above the cutting plane).
        # Volume above plane = π * r² * h - π * r² * (z1 + z2) / 2
        #                    = π * r² * (h - (z1+z2)/2)
        # Set this = (1/3) * π * r² * h:
        #   h - (z1+z2)/2 = h/3
        #   (z1+z2)/2 = 2h/3
        #   z1 + z2 = 4h/3
        #
        # Choose: plane touches x=+r at z = z1, x=-r at z = z2
        # Let z1 = h/2 (top of cylinder at x=+r side) and z2 = 4h/3 - h/2 = 5h/6
        # But z2 = 5h/6 > h/2, so the plane exits above the cylinder on the -x side.
        # That means the cut removes a wedge from the top.
        #
        # Better: let z1 = h/6 and z2 = 7h/6 — but z2 > h/2 again.
        # 
        # Let's reconsider: place z1 at x=+r and z2 at x=-r, both measured from bottom.
        # Cylinder bottom is at z = -h/2, top at z = +h/2.
        # z1 + z2 = 4h/3 means average = 2h/3.
        # Since cylinder height is h, and center is at 0, let's use:
        # z1 = h/2 - 0 = h/2 (plane at top on +x side)
        # z2 = 4h/3 - h/2 = 8h/6 - 3h/6 = 5h/6 > h/2 → outside cylinder
        #
        # This means the plane exits above the cylinder on the -x side,
        # which is fine — the cutting box just needs to be large enough.
        # The intersection with the cylinder removes the correct 1/3.
        #
        # Let me use a simpler parameterization:
        # The cutting plane passes through the cylinder axis at height z_mid from bottom,
        # tilted so one side is at z_low and other at z_high.
        # z_mid (at x=0) = (z1+z2)/2 = 2h/3 from bottom = 2h/3 - h/2 = h/6 in centered coords.
        #
        # The plane equation: z = z_mid_centered + (x/r) * tilt_half
        # where tilt_half = (z2 - z1)/2
        #
        # We need z1 + z2 = 4h/3, and we want the plane to intersect the cylinder nicely.
        # Choose z1 = h/3 (from bottom) = h/3 - h/2 = -h/6 in centered coords (at x=+r)
        # Then z2 = 4h/3 - h/3 = h (from bottom) = h - h/2 = h/2 in centered coords (at x=-r)
        # Check: z2 = h/2 = top of cylinder. ✓ The plane goes from z=-h/6 at x=+r to z=+h/2 at x=-r.
        #
        # z_mid_centered = (z1_c + z2_c)/2 = (-h/6 + h/2)/2 = (2h/6)/2 = h/6
        # tilt_half = (z2_c - z1_c)/2 = (h/2 - (-h/6))/2 = (2h/3)/2 = h/3
        # Plane: z = h/6 - (x/r)*(h/3)  [note: at x=+r, z = h/6 - h/3 = -h/6 ✓]
        #                                 [at x=-r, z = h/6 + h/3 = h/2 ✓]
    
        z_mid = h / 6       # plane center height (in centered coords)
        tilt_half = h / 3   # half the tilt range
    
        # The cutting plane normal: z = z_mid - (x/r)*tilt_half
        # Rearranged: (1/r)*tilt_half * x + z = z_mid
        # Normal vector (unnormalized): (tilt_half/r, 0, 1) = (h/(3r), 0, 1)
        # With h=40, r=10: (4/3, 0, 1)
    
        # --- Step 3: Build the cutting solid ---
        # Create a large box and rotate it to match the cutting plane,
        # then position it to cut away the upper-front portion.
        #
        # The cutting plane: z = h/6 - (x/r)*(h/3)
        # We'll build a box in the XY plane and rotate it.
        # 
        # Angle of tilt: tan(θ) = tilt_half / r = (h/3) / r = 40/3 / 10 = 4/3
        # θ = arctan(4/3) ≈ 53.13°
        # The plane tilts in the XZ plane (rotation about Y axis).
    
        tilt_angle_rad = math.atan2(tilt_half, r)  # arctan((h/3)/r)
        tilt_angle_deg = math.degrees(tilt_angle_rad)
    
        # Build a large cutting box (much larger than cylinder)
        # Start with a flat box in XY, then rotate about Y by tilt_angle,
        # then translate to the correct position.
        #
        # The cutting plane passes through point (0, 0, z_mid) with normal (tilt_half/r, 0, 1).
        # We want to cut ABOVE this plane (remove the upper-left wedge).
        #
        # Strategy: create a box that sits above the cutting plane.
        # The box will be large (3*h x 3*h x 3*h) to ensure it covers the cylinder.
        # We rotate the box so its bottom face aligns with the cutting plane,
        # then position it above.
    
        box_size = 3 * h  # large enough to cover cylinder
    
        # Create cutting box: centered at origin initially
        # We'll use a different approach: create the cutting plane as a Face,
        # then use it to split the cylinder.
        #
        # Simpler approach: use a rotated box as cutter.
        # The cutter box bottom face lies on the cutting plane.
        # 
        # The cutting plane passes through (0, 0, z_mid).
        # Normal direction: n = normalize(tilt_half/r, 0, 1) = normalize(4/3, 0, 1)
        # 
        # Create a box in local coords where XY is the cutting plane:
        # Box extends from z=0 to z=box_size in local Z (above the plane).
        # Then transform to world coords.
    
        # Normal to cutting plane (pointing "above" = direction we remove):
        nx = tilt_half / r   # = h/(3r) = 4/3
        nz = 1.0
        n_len = math.sqrt(nx**2 + nz**2)
        nx_norm = nx / n_len
        nz_norm = nz / n_len
    
        # Rotation angle about Y axis to align local Z with world normal:
        # Local Z = (0,0,1), world normal = (nx_norm, 0, nz_norm)
        # Rotation about Y: angle = arctan2(nx_norm, nz_norm) but we need to be careful
        # Actually: rotate about -Y by angle = arctan2(nx, nz) to tilt +Z toward +X
        # After rotation about Y by angle α: (0,0,1) → (sin α, 0, cos α)
        # We want (sin α, 0, cos α) = (nx_norm, 0, nz_norm)
        # So α = arctan2(nx_norm, nz_norm) = arctan2(4/3, 1) / norm... 
        # Actually α = arctan(nx/nz) = arctan(4/3) ≈ 53.13°
    
        alpha_deg = math.degrees(math.atan2(nx, nz))  # ≈ 53.13°
    
        # Build the cutting box using CadQuery transformations
        # The box is large, centered in XY, extending from 0 to box_size in local Z
        # We place it so its bottom (z=0 face) is on the cutting plane
    
        # Step: create box with bottom at z=0 (centered=False in Z)
        cutter = (
            cq.Workplane("XY")
            .box(box_size, box_size, box_size, centered=(True, True, False))
            .rotate((0, 0, 0), (0, 1, 0), -alpha_deg)   # rotate about Y axis
            .translate((0, 0, z_mid))                     # move to cutting plane center
        )
    
        # --- Step 4: Subtract the cutter from the cylinder ---
        result = cylinder.cut(cutter)
    
        # --- Final object verification ---
        TOL = 0.01
        REL_TOL = 0.02  # 2% relative tolerance for volume
    
        # Check bounding box
        bb = result.val().BoundingBox()
    
        # X and Y extents should still be the full diameter (2r = 20)
        assert abs(bb.xlen - d) < TOL, f"X extent: expected {d}, got {bb.xlen}"
        assert abs(bb.ylen - d) < TOL, f"Y extent: expected {d}, got {bb.ylen}"
    
        # Z extent: the cylinder goes from -h/2 to +h/2 = -20 to +20
        # After cut, the bottom is still at -h/2 = -20
        # The top is cut: at x=0, the plane is at z_mid = h/6 ≈ 6.67
        # At x=-r=-10, the plane is at z=h/2=20 (top of cylinder)
        # So the max Z of the remaining solid is h/2 = 20
        assert abs(bb.zmin - (-h/2)) < TOL, f"Z min: expected {-h/2}, got {bb.zmin}"
        assert abs(bb.zmax - (h/2)) < TOL, f"Z max: expected {h/2}, got {bb.zmax}"
    
        # Volume check: should be 2/3 of original cylinder volume
        full_vol = math.pi * r**2 * h
        expected_vol = (2.0 / 3.0) * full_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < REL_TOL, \
            f"Volume: expected ~{expected_vol:.2f} (2/3 of {full_vol:.2f}), got {actual_vol:.2f}"
    
        # Should have exactly 1 solid
        assert result.solids().size() == 1, f"Expected 1 solid, got {result.solids().size()}"
    
        # Should have a cylindrical face (the curved side of the cylinder)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # Should have planar faces: bottom circle + the angled cut face
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 2, f"Expected at least 2 planar faces, got {planar_faces}"
    
        # The bottom face should be at z = -h/2
        bottom_face_z = result.faces("<Z").val().Center().z
        assert abs(bottom_face_z - (-h/2)) < TOL, \
            f"Bottom face Z center: expected {-h/2}, got {bottom_face_z}"
    
        # Center of mass should be below z=0 (since upper portion was removed)
        com = cq.Shape.centerOfMass(result.val())
        assert com.z < 0, f"Center of mass Z should be negative (below mid), got {com.z}"
    
        # The point at (0, 0, z_mid + 0.1) should be OUTSIDE (it was cut away)
        assert not result.val().isInside((0, 0, z_mid + 0.1)), \
            f"Point above cutting plane should be outside the solid"
    
        # The point at (0, 0, z_mid - 1) should be INSIDE
        assert result.val().isInside((0, 0, z_mid - 1)), \
            f"Point below cutting plane should be inside the solid"
    
        print(f"✓ Cylinder: r={r}, d={d}, h={h}")
        print(f"✓ Full volume: {full_vol:.2f}, Expected 2/3: {expected_vol:.2f}, Actual: {actual_vol:.2f}")
        print(f"✓ Tilt angle: {alpha_deg:.2f}°")
        print(f"✓ Bounding box: x={bb.xlen:.2f}, y={bb.ylen:.2f}, z={bb.zlen:.2f}")
        print(f"✓ Center of mass: ({com.x:.2f}, {com.y:.2f}, {com.z:.2f})")
        print(f"✓ Planar faces: {planar_faces}, Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00036518/gpt_generated.stl')
