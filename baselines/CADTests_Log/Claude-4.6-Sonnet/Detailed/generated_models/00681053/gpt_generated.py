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
        page_length = 0.46077   # X extent of each page
        page_width  = 0.75      # Y extent (spine direction)
        page_height = 0.048077  # thickness of each page
    
        # Dihedral angle between the two pages (obtuse)
        # Total opening angle = 150 degrees
        # Each page is 75 degrees from the spine (Z-axis)
        # i.e., each page is rotated 15 degrees above the horizontal XY plane
        half_angle_from_horizontal = 15.0  # degrees above XY plane
        angle_rad = math.radians(half_angle_from_horizontal)
    
        # --- Step 1: Create the right page ---
        # centered=(False, True, True): X from 0 to page_length, Y centered, Z centered
        right_page = (
            cq.Workplane("XY")
            .box(page_length, page_width, page_height,
                 centered=(False, True, True))
        )
    
        # Rotate right page about Y-axis by -half_angle_from_horizontal
        # Rotation by θ=-15° about Y: x'=x·cos15-z·sin15, z'=x·sin15+z·cos15
        right_page = right_page.rotate((0, 0, 0), (0, 1, 0), -half_angle_from_horizontal)
    
        # --- Step 2: Create the left page ---
        # Box with right edge at x=0, extending in -X
        left_page = (
            cq.Workplane("XY")
            .box(page_length, page_width, page_height,
                 centered=(False, True, True))
            .translate((-page_length, 0, 0))  # shift so right edge is at x=0
        )
    
        # Rotate left page about Y-axis by +half_angle_from_horizontal
        # Rotation by θ=+15° about Y: x'=x·cos15+z·sin15, z'=-x·sin15+z·cos15
        left_page = left_page.rotate((0, 0, 0), (0, 1, 0), half_angle_from_horizontal)
    
        # --- Step 3: Union the two pages ---
        # They share the spine edge at x=0, y in [-0.375, 0.375], z=0
        result = right_page.union(left_page)
    
        # --- Final object verification ---
        TOL = 0.01
    
        solid = result.val()
    
        # Volume check: two pages, each = page_length * page_width * page_height
        single_page_vol = page_length * page_width * page_height
        expected_vol = 2 * single_page_vol
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        bb = solid.BoundingBox()
    
        # Y extent = page_width (no rotation about X or Z)
        assert abs(bb.ylen - page_width) < TOL, \
            f"Y extent (width): expected {page_width}, got {bb.ylen}"
    
        # X extent:
        # Right page rotation θ=-15°: x' = x·cos15 - z·sin15
        # Corners (x,z): (0,±h/2), (L,±h/2)
        # Max x' = L·cos15 + (h/2)·sin15  [from corner (L, -h/2)]
        # By symmetry left page gives same magnitude on negative side
        # Total X = 2*(L·cos15 + (h/2)·sin15)
        expected_xlen = 2 * (page_length * math.cos(angle_rad) + (page_height / 2) * math.sin(angle_rad))
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X extent: expected {expected_xlen:.5f}, got {bb.xlen:.5f}"
    
        # Z extent:
        # Right page rotation θ=-15°: z' = x·sin15 + z·cos15
        # Corners: (0,-h/2)→z'=-h/2·cos15, (L,+h/2)→z'=L·sin15+h/2·cos15
        # Left page rotation θ=+15°: z' = -x·sin15 + z·cos15
        # (-L,+h/2)→z'=L·sin15+h/2·cos15, (0,-h/2)→z'=-h/2·cos15
        # Combined: max z' = L·sin15 + h/2·cos15, min z' = -h/2·cos15
        # Z extent = L·sin15 + h/2·cos15 + h/2·cos15 = L·sin15 + h·cos15
        expected_zlen = page_length * math.sin(angle_rad) + page_height * math.cos(angle_rad)
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z extent: expected {expected_zlen:.5f}, got {bb.zlen:.5f}"
    
        # X symmetry: center of bounding box should be near x=0
        cx = (bb.xmin + bb.xmax) / 2
        assert abs(cx) < TOL, f"X center should be ~0, got {cx}"
    
        # Z center: (max_z + min_z)/2 = (L·sin15 + h/2·cos15 + (-h/2·cos15))/2 = L·sin15/2
        expected_cz = page_length * math.sin(angle_rad) / 2
        cz = (bb.zmin + bb.zmax) / 2
        assert abs(cz - expected_cz) < TOL, f"Z center should be ~{expected_cz:.5f}, got {cz:.5f}"
    
        # Check that points inside each page are inside the solid
        # Center of right page after rotation: midpoint along page at (L/2, 0) rotated
        inside_right = (page_length * math.cos(angle_rad) * 0.5,
                        0,
                        page_length * math.sin(angle_rad) * 0.5)
        assert solid.isInside(inside_right, tolerance=0.001), \
            f"Point inside right page should be inside solid: {inside_right}"
    
        inside_left = (-page_length * math.cos(angle_rad) * 0.5,
                       0,
                       page_length * math.sin(angle_rad) * 0.5)
        assert solid.isInside(inside_left, tolerance=0.001), \
            f"Point inside left page should be inside solid: {inside_left}"
    
        # Face count: 6 faces per page = 12 total, but the union merges the two
        # inner end-faces at the spine (they share an edge and the topology merges
        # adjacent coplanar regions), resulting in 10 faces total.
        face_count = result.faces().size()
        assert face_count == 10, \
            f"Face count: expected 10, got {face_count}"
    
        # Planar face count: all faces of flat page boxes are planar
        planar_count = result.faces("%Plane").size()
        assert planar_count == 10, \
            f"Planar face count: expected 10, got {planar_count}"
    
        # No cylindrical faces (no holes or curved surfaces)
        cyl_count = result.faces("%Cylinder").size()
        assert cyl_count == 0, \
            f"Cylindrical face count: expected 0, got {cyl_count}"
    
        print(f"All assertions passed!")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"BBox: X={bb.xlen:.5f}, Y={bb.ylen:.5f}, Z={bb.zlen:.5f}")
        print(f"Face count: {face_count}, Planar: {planar_count}, Cylindrical: {cyl_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00681053/gpt_generated.stl')
