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
        # --- Step 1: Define the polyline points (in meters, on XY plane) ---
        points = [
            (-0.05430806,  0.05735744),
            (-0.05430806, -0.05851911),
            (-0.04704762, -0.05851911),
            (-0.0383351,  -0.00217813),
            ( 0.00232334, -0.00217813),
            ( 0.0116167,  -0.06200412),
            ( 0.01742505, -0.06200412),
            ( 0.01452087,  0.01030982),
            (-0.02875133,  0.01030982),
            (-0.0450147,   0.05735744),
            (-0.05430806,  0.05735744),  # closing back to start
        ]
    
        # --- Step 2: Build the closed polyline and extrude along Z ---
        # Use the Workplane wire/polyline approach
        # We'll build the profile using lineTo calls
    
        # Start from the first point
        wp = cq.Workplane("XY")
    
        # Move to start point and draw the polyline
        wp = wp.moveTo(points[0][0], points[0][1])
        for pt in points[1:]:
            wp = wp.lineTo(pt[0], pt[1])
    
        # Close the wire (back to start)
        wp = wp.close()
    
        # --- Step 3: Extrude along Z-axis by 0.1016 meters ---
        extrusion_height = 0.1016
        result = wp.extrude(extrusion_height)
    
        # --- Step 4: Scale by factor 7.38186180173805 ---
        scale_factor = 7.38186180173805
    
        # Use CadQuery's scale via direct OCCT transformation
        # CadQuery doesn't have a direct .scale() on Workplane, use the Shape API
        solid = result.val()
    
        # Scale using the OCCT BRepBuilderAPI_Transform
        from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
        from OCP.gp import gp_Trsf, gp_Pnt
    
        trsf_scale = gp_Trsf()
        trsf_scale.SetScale(gp_Pnt(0, 0, 0), scale_factor)
        builder = BRepBuilderAPI_Transform(solid.wrapped, trsf_scale, True)
        scaled_shape = cq.Shape(builder.Shape())
    
        # --- Step 5: Rotate -90 degrees around X-axis ---
        # Then -90 degrees around Z-axis
        from OCP.gp import gp_Ax1, gp_Dir
    
        # Rotation around X-axis by -90 degrees
        trsf_rx = gp_Trsf()
        ax_x = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
        trsf_rx.SetRotation(ax_x, math.radians(-90))
        builder_rx = BRepBuilderAPI_Transform(scaled_shape.wrapped, trsf_rx, True)
        rotated_x_shape = cq.Shape(builder_rx.Shape())
    
        # Rotation around Z-axis by -90 degrees
        trsf_rz = gp_Trsf()
        ax_z = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
        trsf_rz.SetRotation(ax_z, math.radians(-90))
        builder_rz = BRepBuilderAPI_Transform(rotated_x_shape.wrapped, trsf_rz, True)
        rotated_z_shape = cq.Shape(builder_rz.Shape())
    
        # Wrap back into a Workplane
        result = cq.Workplane("XY").add(rotated_z_shape)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Get the final solid
        final_solid = result.val()
        bb = final_solid.BoundingBox()
    
        print(f"Bounding box: X=[{bb.xmin:.4f}, {bb.xmax:.4f}], Y=[{bb.ymin:.4f}, {bb.ymax:.4f}], Z=[{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"Dimensions: xlen={bb.xlen:.4f}, ylen={bb.ylen:.4f}, zlen={bb.zlen:.4f}")
        print(f"Volume: {final_solid.Volume():.6f}")
    
        # Compute expected dimensions from the original points
        # Original X range: min=-0.05430806, max=0.01742505 → xlen=0.07173311
        # Original Y range: min=-0.06200412, max=0.05735744 → ylen=0.11936156
        # Original Z range: 0 to 0.1016
    
        orig_x_min = min(p[0] for p in points)
        orig_x_max = max(p[0] for p in points)
        orig_y_min = min(p[1] for p in points)
        orig_y_max = max(p[1] for p in points)
        orig_z_min = 0.0
        orig_z_max = extrusion_height
    
        # After scaling:
        s = scale_factor
        sx_min = orig_x_min * s
        sx_max = orig_x_max * s
        sy_min = orig_y_min * s
        sy_max = orig_y_max * s
        sz_min = orig_z_min * s
        sz_max = orig_z_max * s
    
        # After rotation -90° around X: (x,y,z) → (x, z, -y)
        # x stays: [sx_min, sx_max]
        # new_y = z: [sz_min, sz_max]
        # new_z = -y: [-sy_max, -sy_min]
        rx_x_min, rx_x_max = sx_min, sx_max
        rx_y_min, rx_y_max = sz_min, sz_max
        rx_z_min, rx_z_max = -sy_max, -sy_min
    
        # After rotation -90° around Z: (x,y,z) → (y, -x, z)
        # new_x = y: [rx_y_min, rx_y_max]
        # new_y = -x: [-rx_x_max, -rx_x_min]
        # new_z = z: [rx_z_min, rx_z_max]
        final_x_min = rx_y_min
        final_x_max = rx_y_max
        final_y_min = -rx_x_max
        final_y_max = -rx_x_min
        final_z_min = rx_z_min
        final_z_max = rx_z_max
    
        exp_xlen = final_x_max - final_x_min
        exp_ylen = final_y_max - final_y_min
        exp_zlen = final_z_max - final_z_min
    
        print(f"\nExpected dimensions: xlen={exp_xlen:.4f}, ylen={exp_ylen:.4f}, zlen={exp_zlen:.4f}")
    
        # Check bounding box dimensions
        assert abs(bb.xlen - exp_xlen) < TOL, f"X length: expected {exp_xlen:.4f}, got {bb.xlen:.4f}"
        assert abs(bb.ylen - exp_ylen) < TOL, f"Y length: expected {exp_ylen:.4f}, got {bb.ylen:.4f}"
        assert abs(bb.zlen - exp_zlen) < TOL, f"Z length: expected {exp_zlen:.4f}, got {bb.zlen:.4f}"
    
        # Volume check: compute approximate 2D area of the 'h' profile
        # Use shoelace formula for the polygon area
        n = len(points) - 1  # last point = first point (closed)
        poly = points[:n]  # unique points
        area_2d = 0.0
        for i in range(n):
            j = (i + 1) % n
            area_2d += poly[i][0] * poly[j][1]
            area_2d -= poly[j][0] * poly[i][1]
        area_2d = abs(area_2d) / 2.0
    
        expected_vol = area_2d * extrusion_height * (s ** 3)
        actual_vol = final_solid.Volume()
        print(f"\nExpected volume (approx): {expected_vol:.6f}")
        print(f"Actual volume: {actual_vol:.6f}")
    
        # Volume should be positive and roughly match
        assert actual_vol > 0, f"Volume should be positive, got {actual_vol}"
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.4f}, got {actual_vol:.4f}"
    
        # Check that the solid has faces (it's a valid solid)
        face_count = result.faces().size()
        print(f"Face count: {face_count}")
        assert face_count >= 4, f"Expected at least 4 faces, got {face_count}"
    
        # Check the solid is valid (non-zero volume)
        assert final_solid.Volume() > 0, "Solid must have positive volume"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00037135/gpt_generated.stl')
