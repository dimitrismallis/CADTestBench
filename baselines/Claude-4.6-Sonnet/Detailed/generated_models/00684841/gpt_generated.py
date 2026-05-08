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
        outer_radius = 0.18
        inner_radius = 0.17  # marginally smaller to create hollow
    
        # Sector angle - "minor sector" means less than 180 degrees, use 90 degrees
        sector_angle_deg = 90.0
        sector_angle_rad = math.radians(sector_angle_deg)
    
        # Rectangle path dimensions
        rect_width = 0.0075    # X dimension
        rect_height = 0.750037 # Y dimension
        # Centered at (-0.00375, 0)
        rect_cx = -0.00375
        rect_cy = 0.0
    
        # --- Step 1: Helper to compute sector arc points on XZ plane ---
        def make_sector_arc_points(radius, angle_deg):
            angle_rad = math.radians(angle_deg)
            start_x = radius
            start_z = 0.0
            end_x = radius * math.cos(angle_rad)
            end_z = radius * math.sin(angle_rad)
            mid_angle = angle_rad / 2
            mid_x = radius * math.cos(mid_angle)
            mid_z = radius * math.sin(mid_angle)
            return (start_x, start_z), (mid_x, mid_z), (end_x, end_z)
    
        # --- Step 2: Create the sweep path (rectangle on XY plane) ---
        path = (
            cq.Workplane("XY")
            .center(rect_cx, rect_cy)
            .rect(rect_width, rect_height)
            .consolidateWires()
        )
        path_wire = path.vals()[0]
    
        # --- Step 3: Create outer sector profile and sweep ---
        arc_start, arc_mid, arc_end = make_sector_arc_points(outer_radius, sector_angle_deg)
    
        outer_profile = (
            cq.Workplane("XZ")
            .moveTo(0, 0)
            .lineTo(arc_start[0], arc_start[1])
            .threePointArc((arc_mid[0], arc_mid[1]), (arc_end[0], arc_end[1]))
            .close()
        )
    
        outer_solid = outer_profile.sweep(path_wire, makeSolid=True)
    
        # --- Step 4: Create inner sector profile for cutting ---
        inner_arc_start, inner_arc_mid, inner_arc_end = make_sector_arc_points(inner_radius, sector_angle_deg)
    
        inner_profile = (
            cq.Workplane("XZ")
            .moveTo(0, 0)
            .lineTo(inner_arc_start[0], inner_arc_start[1])
            .threePointArc((inner_arc_mid[0], inner_arc_mid[1]), (inner_arc_end[0], inner_arc_end[1]))
            .close()
        )
    
        inner_solid = inner_profile.sweep(path_wire, makeSolid=True)
    
        # --- Step 5: Cut inner from outer to create hollow sector ---
        result = outer_solid.cut(inner_solid)
    
        # --- Step 6: Translate to (0.180047, -0.375015, 0) ---
        result = result.translate((0.180047, -0.375015, 0))
    
        # --- Step 7: Rotate 180 degrees around Z-axis ---
        result = result.rotate((0, 0, 0), (0, 0, 1), 180)
    
        # --- Final object verification ---
        TOL = 0.005
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        print(f"Bounding box:")
        print(f"  X: [{bb.xmin:.6f}, {bb.xmax:.6f}], xlen={bb.xlen:.6f}")
        print(f"  Y: [{bb.ymin:.6f}, {bb.ymax:.6f}], ylen={bb.ylen:.6f}")
        print(f"  Z: [{bb.zmin:.6f}, {bb.zmax:.6f}], zlen={bb.zlen:.6f}")
        print(f"Volume: {solid.Volume():.8f}")
    
        # The sector profile (radius 0.18) is swept along the rectangle perimeter.
        # The profile extends outward from the path by outer_radius on each side:
        #   xlen ≈ rect_width  + 2 * outer_radius = 0.0075 + 0.36 = 0.3675
        #   ylen ≈ rect_height + 2 * outer_radius = 0.750037 + 0.36 = 1.110037
        # After 180° rotation around Z, xlen and ylen are preserved.
        expected_xlen = rect_width + 2 * outer_radius   # 0.3675
        expected_ylen = rect_height + 2 * outer_radius  # 1.110037
        expected_zlen = outer_radius                     # 0.18
    
        # 1. Bounding box X extent
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X extent should be ~{expected_xlen:.4f}, got {bb.xlen:.6f}"
    
        # 2. Bounding box Y extent
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y extent should be ~{expected_ylen:.4f}, got {bb.ylen:.6f}"
    
        # 3. Bounding box Z extent = outer_radius (sector height)
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z extent should be ~{expected_zlen:.4f}, got {bb.zlen:.6f}"
    
        # 4. Z bounds: rotation around Z and translation with Z=0 don't change Z range
        assert abs(bb.zmin) < TOL, \
            f"Z min should be ~0, got {bb.zmin:.6f}"
        assert abs(bb.zmax - outer_radius) < TOL, \
            f"Z max should be ~{outer_radius:.4f}, got {bb.zmax:.6f}"
    
        # 5. Volume must be positive
        assert solid.Volume() > 0, \
            f"Volume must be positive, got {solid.Volume()}"
    
        # 6. Volume bounds check
        outer_sector_area = 0.5 * outer_radius**2 * sector_angle_rad
        inner_sector_area = 0.5 * inner_radius**2 * sector_angle_rad
        shell_area = outer_sector_area - inner_sector_area
        rect_perimeter = 2 * (rect_width + rect_height)
        approx_vol_lower = shell_area * rect_height * 0.3   # conservative lower
        approx_vol_upper = outer_sector_area * rect_perimeter * 3.0  # generous upper
        print(f"Volume bounds: [{approx_vol_lower:.6f}, {approx_vol_upper:.6f}]")
        assert solid.Volume() > approx_vol_lower, \
            f"Volume {solid.Volume():.6f} below lower bound {approx_vol_lower:.6f}"
        assert solid.Volume() < approx_vol_upper, \
            f"Volume {solid.Volume():.6f} above upper bound {approx_vol_upper:.6f}"
    
        # 7. Should have cylindrical faces (inner and outer curved surfaces of the hollow sector)
        cyl_face_count = result.faces("%Cylinder").size()
        print(f"Cylindrical faces: {cyl_face_count}")
        assert cyl_face_count >= 2, \
            f"Expected at least 2 cylindrical faces (inner+outer), got {cyl_face_count}"
    
        # 8. Should have planar faces (flat sides of the sector)
        planar_face_count = result.faces("%Plane").size()
        print(f"Planar faces: {planar_face_count}")
        assert planar_face_count >= 2, \
            f"Expected at least 2 planar faces, got {planar_face_count}"
    
        # 9. The object should be a single solid
        solid_count = result.solids().size()
        print(f"Solid count: {solid_count}")
        assert solid_count == 1, \
            f"Expected 1 solid, got {solid_count}"
    
        # 10. After 180° rotation around Z the object is mostly in negative X territory.
        # The small positive X contribution (~rect_width/2) is acceptable.
        # xmax should be no larger than rect_width + TOL
        assert bb.xmax < rect_width + TOL, \
            f"After 180° rotation, X max should be <= rect_width ({rect_width:.4f}), got {bb.xmax:.6f}"
    
        # 11. After 180° rotation, Y should be mostly positive.
        # ymin should be no more negative than outer_radius (the sector overhang)
        assert bb.ymin > -(outer_radius + TOL), \
            f"After 180° rotation, Y min should be > -{outer_radius:.4f}, got {bb.ymin:.6f}"
    
        # 12. Center of mass: Z should be between 0 and outer_radius
        center = cq.Shape.centerOfMass(solid)
        print(f"Center of mass: ({center.x:.4f}, {center.y:.4f}, {center.z:.4f})")
        assert 0 < center.z < outer_radius, \
            f"Z center of mass should be in (0, {outer_radius}), got {center.z:.4f}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00684841/gpt_generated.stl')
