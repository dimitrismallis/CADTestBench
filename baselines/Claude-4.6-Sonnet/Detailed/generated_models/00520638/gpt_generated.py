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
        L = 1.10769       # base length (X)
        W = 0.474725      # base width (Y)
        H = 0.18989       # base height (Z)
    
        cyl_d = L / 2     # cylinder diameter ≈ 0.553845
        cyl_r = cyl_d / 2
        cyl_h = W         # cylinder height = 0.474725
    
        conn_d = cyl_d    # connector box side = cylinder diameter
        conn_h = cyl_h / 2  # connector height = 0.237363
    
        inner_d = 0.194358
        inner_r = inner_d / 2
    
        # --- Step 1: Base box centered at origin ---
        # Base: L x W x H, centered at (0, 0, 0), top face at z = H/2
        base = cq.Workplane("XY").box(L, W, H)
    
        # --- Step 2: Outer cylinder on top of base ---
        # Cylinder centered at (0, 0), sitting on top of base
        # Base top is at z = H/2
        # Cylinder goes from z = H/2 to z = H/2 + cyl_h
        # "partially protrudes" - cylinder is centered at x=0, y=0
        # The cylinder diameter (0.5538) < base width (0.4747)? No, cyl_d > W
        # So cylinder protrudes beyond the base in Y direction
        cyl_center_z = H/2 + cyl_h/2
        outer_cyl = cq.Workplane("XY").workplane(offset=H/2).circle(cyl_r).extrude(cyl_h)
    
        # --- Step 3: Connector box on top of cylinder ---
        # Connector: conn_d x conn_d x conn_h, centered on top of cylinder
        conn_top_z = H/2 + cyl_h + conn_h/2
        connector = cq.Workplane("XY").workplane(offset=H/2 + cyl_h).box(conn_d, conn_d, conn_h, centered=(True, True, False))
    
        # --- Step 4: Union base + cylinder + connector ---
        assembly = base.union(outer_cyl).union(connector)
    
        # --- Step 5: Subtract inner cylinder ---
        # Inner cylinder through center, along Z axis, full height
        total_h = H + cyl_h + conn_h
        inner_cyl = cq.Workplane("XY").workplane(offset=-total_h).circle(inner_r).extrude(total_h * 3)
        assembly = assembly.cut(inner_cyl)
    
        # --- Step 6: Subtract inner box ---
        # Inner box: inner_d x inner_d, cuts through center of cylinder and connector
        # Position: centered at x=0, y=0, cutting through the cylinder+connector region
        inner_box_h = cyl_h + conn_h + 0.1  # enough to cut through cylinder and connector
        inner_box = cq.Workplane("XY").workplane(offset=H/2 - 0.05).box(inner_d, inner_d, inner_box_h + 0.1, centered=(True, True, False))
        assembly = assembly.cut(inner_box)
    
        # --- Step 7: Arm as polyline ---
        # Points: [(0, 0.316484), (-0.056, 0.483119), (L/2, 0.613244), (L/2, 0.434708)]
        # These are (x, z) coordinates in the XZ plane (arm extends along Y/width)
        # The arm is extruded along the width of the base (Y direction)
        # We need to close the polyline to form a face
    
        arm_pts = [
            (0, 0.316484),
            (-0.056, 0.483119),
            (L/2, 0.613244),
            (L/2, 0.434708),
        ]
    
        # Close the polyline by connecting last point back to first
        # Build the arm profile in XZ plane, extrude along Y
        arm_profile = (
            cq.Workplane("XZ")
            .moveTo(arm_pts[0][0], arm_pts[0][1])
            .lineTo(arm_pts[1][0], arm_pts[1][1])
            .lineTo(arm_pts[2][0], arm_pts[2][1])
            .lineTo(arm_pts[3][0], arm_pts[3][1])
            .close()
            .extrude(W)
        )
    
        # Center the arm extrusion in Y (extrude goes in +Y by default from XZ plane)
        # XZ plane extrudes in -Y direction by default in CadQuery
        # Translate to center it: move by -W/2 in Y
        arm_profile = arm_profile.translate((0, -W/2, 0))
    
        # --- Step 8: Union arm with assembly ---
        assembly = assembly.union(arm_profile)
    
        # --- Step 9: Rotate and translate to final position ---
        # Rotate 90 degrees about X axis to align (common for such parts)
        # Then translate as needed
        # Based on the description, rotate so the cylinder axis is horizontal
        result = assembly.rotate((0, 0, 0), (1, 0, 0), -90)
        # Translate to position (center at origin after rotation)
        result = result.translate((0, 0, 0))
    
        # --- Final object verification ---
        TOL = 0.05
    
        bb = result.val().BoundingBox()
    
        # After -90° rotation about X: X stays, Y->Z, Z->-Y
        # Original: X in [-L/2, L/2], Y in [-W/2, W/2], Z in [various]
        # After rotation: X same, new_Y = old_Z, new_Z = -old_Y
    
        # Check bounding box is reasonable
        assert bb.xlen > 0, f"X extent should be positive, got {bb.xlen}"
        assert bb.ylen > 0, f"Y extent should be positive, got {bb.ylen}"
        assert bb.zlen > 0, f"Z extent should be positive, got {bb.zlen}"
    
        # X extent should be approximately L (base length)
        assert abs(bb.xlen - L) < TOL, f"X extent: expected ~{L}, got {bb.xlen}"
    
        # Volume check: base + cylinder + connector - inner_cyl - inner_box + arm
        base_vol = L * W * H
        cyl_vol = math.pi * cyl_r**2 * cyl_h
        conn_vol = conn_d * conn_d * conn_h
        inner_cyl_vol = math.pi * inner_r**2 * (H + cyl_h + conn_h)
        inner_box_vol_approx = inner_d * inner_d * (cyl_h + conn_h)
    
        actual_vol = result.val().Volume()
        assert actual_vol > 0, f"Volume should be positive, got {actual_vol}"
    
        # The volume should be in a reasonable range
        min_vol = base_vol * 0.5
        max_vol = (base_vol + cyl_vol + conn_vol) * 2.0
        assert min_vol < actual_vol < max_vol, f"Volume {actual_vol:.4f} out of expected range [{min_vol:.4f}, {max_vol:.4f}]"
    
        # Check we have cylindrical faces (from the outer cylinder)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # Check we have multiple solids or a compound (should be one unified solid)
        solids = result.solids().size()
        assert solids >= 1, f"Expected at least 1 solid, got {solids}"
    
        # Check the part has planar faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 6, f"Expected at least 6 planar faces, got {planar_faces}"
    
        print(f"Bounding box: X={bb.xlen:.4f}, Y={bb.ylen:.4f}, Z={bb.zlen:.4f}")
        print(f"Volume: {actual_vol:.4f}")
        print(f"Cylindrical faces: {cyl_faces}")
        print(f"Planar faces: {planar_faces}")
        print(f"Solids: {solids}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00520638/gpt_generated.stl')
