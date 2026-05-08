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
        overall_width   = 80.0   # total width of the U-shape
        overall_height  = 60.0   # total height of the U-shape
        col_width       = 15.0   # width of each vertical column
        horiz_thickness = 10.0   # thickness of the horizontal top section
        depth           = 40.0   # extrusion depth (Y direction)
    
        # Derived
        inner_width = overall_width - 2 * col_width   # 50mm gap between columns
        col_height  = overall_height                   # columns run full height
        horiz_bottom_z = overall_height - horiz_thickness  # z=50
    
        # --- Step 1: Draw the U-shaped profile on the XZ plane ---
        # The profile is a closed polygon representing the upside-down U:
        #   - Two tall columns on left and right
        #   - A horizontal bar connecting them at the top
        #
        # 8 vertices, 8 edges → 8 lateral faces + 2 end faces = 10 planar faces total
        #
        # Vertices (going around the profile):
        #   (0,0) -> (col_width,0) -> (col_width, horiz_bottom_z)
        #   -> (overall_width-col_width, horiz_bottom_z)
        #   -> (overall_width-col_width, 0) -> (overall_width, 0)
        #   -> (overall_width, overall_height) -> (0, overall_height) -> close
    
        profile_pts = [
            (0,                         0),                    # bottom-left outer
            (col_width,                 0),                    # bottom-left inner
            (col_width,                 horiz_bottom_z),       # top of inner-left column
            (overall_width - col_width, horiz_bottom_z),       # top of inner-right column
            (overall_width - col_width, 0),                    # bottom-right inner
            (overall_width,             0),                    # bottom-right outer
            (overall_width,             overall_height),       # top-right outer
            (0,                         overall_height),       # top-left outer
        ]
    
        # Draw the closed profile using polyline on XZ plane
        result = (
            cq.Workplane("XZ")
            .moveTo(profile_pts[0][0], profile_pts[0][1])
            .lineTo(profile_pts[1][0], profile_pts[1][1])
            .lineTo(profile_pts[2][0], profile_pts[2][1])
            .lineTo(profile_pts[3][0], profile_pts[3][1])
            .lineTo(profile_pts[4][0], profile_pts[4][1])
            .lineTo(profile_pts[5][0], profile_pts[5][1])
            .lineTo(profile_pts[6][0], profile_pts[6][1])
            .lineTo(profile_pts[7][0], profile_pts[7][1])
            .close()
            .extrude(depth)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - overall_width)  < TOL, \
            f"X length: expected {overall_width}, got {bb.xlen}"
        assert abs(bb.ylen - depth)          < TOL, \
            f"Y length (depth): expected {depth}, got {bb.ylen}"
        assert abs(bb.zlen - overall_height) < TOL, \
            f"Z length (height): expected {overall_height}, got {bb.zlen}"
    
        # Volume check:
        # U-shape area = 2*(col_width * overall_height) + (inner_width * horiz_thickness)
        u_area = 2 * (col_width * overall_height) + (inner_width * horiz_thickness)
        expected_vol = u_area * depth
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Face count:
        # The U-profile has 8 edges → 8 lateral (side) faces when extruded
        # Plus 2 end faces (front and back) = 10 planar faces total
        n_faces = result.faces("%Plane").size()
        assert n_faces == 10, \
            f"Planar face count: expected 10, got {n_faces}"
    
        # Column width > horizontal section thickness (design requirement)
        assert col_width > horiz_thickness, \
            f"Column width ({col_width}) should be > horizontal thickness ({horiz_thickness})"
    
        # The inner cutout: check that a point inside the gap is NOT inside the solid
        # Gap center: x = overall_width/2, z = horiz_bottom_z/2
        gap_x = overall_width / 2        # 40 — center of gap horizontally
        gap_z = horiz_bottom_z / 2       # 25 — midway up the gap
        gap_y = (bb.ymin + bb.ymax) / 2  # midpoint in depth direction
    
        gap_point = cq.Vector(gap_x, gap_y, gap_z)
        assert not result.val().isInside(gap_point), \
            f"Point {gap_point} should be in the gap (outside solid), but isInside returned True"
    
        # Check that a point inside the left column IS inside the solid
        col_x = col_width / 2            # 7.5 — inside left column
        col_z = overall_height / 2       # 30 — midway up
        col_y = gap_y
        col_point = cq.Vector(col_x, col_y, col_z)
        assert result.val().isInside(col_point), \
            f"Point {col_point} should be inside left column, but isInside returned False"
    
        # Check that a point inside the horizontal bar IS inside the solid
        bar_x = overall_width / 2                    # 40 — center horizontally
        bar_z = overall_height - horiz_thickness / 2 # 55 — inside the top bar
        bar_y = gap_y
        bar_point = cq.Vector(bar_x, bar_y, bar_z)
        assert result.val().isInside(bar_point), \
            f"Point {bar_point} should be inside horizontal bar, but isInside returned False"
    
        # Check that a point inside the right column IS inside the solid
        rcol_x = overall_width - col_width / 2  # 72.5 — inside right column
        rcol_z = overall_height / 4             # 15 — lower portion
        rcol_y = gap_y
        rcol_point = cq.Vector(rcol_x, rcol_y, rcol_z)
        assert result.val().isInside(rcol_point), \
            f"Point {rcol_point} should be inside right column, but isInside returned False"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00985066/gpt_generated.stl')
