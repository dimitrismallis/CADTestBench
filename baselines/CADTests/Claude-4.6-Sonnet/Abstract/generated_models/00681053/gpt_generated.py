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
        page_width = 80.0        # width of each page (from spine outward)
        book_depth = 120.0       # depth of the book (extrusion length, Y-axis)
        page_thickness = 3.0     # thickness of each page
        opening_angle_deg = 150.0  # obtuse angle between the two pages
    
        # Half-angle from the vertical (Z-axis) for each page
        half_angle_rad = math.radians(opening_angle_deg / 2.0)  # 75 degrees
    
        sa = math.sin(half_angle_rad)  # sin(75°) ≈ 0.9659
        ca = math.cos(half_angle_rad)  # cos(75°) ≈ 0.2588
    
        # --- Step 1: Compute corner points of the two-page cross-section (XZ plane) ---
        # Right page: direction (sa, ca), thickness direction (ca, -sa)
        r_inner_near = ( 0.0,                                    0.0                                   )
        r_inner_far  = ( page_width * sa,                        page_width * ca                       )
        r_outer_far  = ( page_width * sa + page_thickness * ca,  page_width * ca - page_thickness * sa )
        r_outer_near = ( page_thickness * ca,                   -page_thickness * sa                   )
    
        # Left page: mirror in X
        l_inner_near = ( 0.0,                                    0.0                                   )
        l_inner_far  = (-page_width * sa,                        page_width * ca                       )
        l_outer_far  = (-page_width * sa - page_thickness * ca,  page_width * ca - page_thickness * sa )
        l_outer_near = (-page_thickness * ca,                   -page_thickness * sa                   )
    
        # --- Step 2: Build a single closed polygon that correctly traces both thin strips ---
        # Key insight: the path must go THROUGH the spine point (0,0) to avoid
        # enclosing the large open V-shaped interior between the pages.
        #
        # Trace (in XZ plane):
        #   r_outer_near -> r_outer_far -> r_inner_far -> spine(0,0) ->
        #   l_inner_far -> l_outer_far -> l_outer_near -> close (back to r_outer_near)
        #
        # The closing segment from l_outer_near to r_outer_near passes through the
        # bottom of the spine, which is a short segment at the base.
    
        profile_pts = [
            r_outer_near,       # ( ca*t,          -sa*t )         spine bottom-right
            r_outer_far,        # ( w*sa + ca*t,    w*ca - sa*t )  right page outer tip
            r_inner_far,        # ( w*sa,           w*ca )         right page inner tip
            r_inner_near,       # ( 0,              0 )            spine top (origin)
            l_inner_far,        # (-w*sa,           w*ca )         left page inner tip
            l_outer_far,        # (-w*sa - ca*t,    w*ca - sa*t )  left page outer tip
            l_outer_near,       # (-ca*t,          -sa*t )         spine bottom-left
        ]
    
        # --- Step 3: Extrude the single closed profile along Y ---
        result = (
            cq.Workplane("XZ")
            .polyline(profile_pts)
            .close()
            .extrude(book_depth)
        )
    
        # --- Final object verification ---
        TOL = 0.5
    
        bb = result.val().BoundingBox()
    
        # X extent: from left outer to right outer
        expected_xlen = 2.0 * (page_width * sa + page_thickness * ca)
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen:.3f}, got {bb.xlen:.3f}"
    
        # Z extent: from bottom of spine to top of pages
        expected_zmax = page_width * ca          # top of pages
        expected_zmin = -page_thickness * sa     # bottom of spine
        expected_zlen = expected_zmax - expected_zmin
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen:.3f}, got {bb.zlen:.3f}"
    
        # Y extent: book depth
        assert abs(bb.ylen - book_depth) < TOL, \
            f"Y (book depth): expected {book_depth:.1f}, got {bb.ylen:.3f}"
    
        # Volume: 2 pages each = page_width * page_thickness * book_depth
        # The two pages share only the spine edge (zero volume overlap)
        expected_vol = 2.0 * page_width * page_thickness * book_depth
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Should have exactly 1 solid (single connected extrusion)
        assert result.solids().size() == 1, \
            f"Solids: expected 1, got {result.solids().size()}"
    
        # X symmetry: spine is centered at X=0
        assert abs(bb.xmin + bb.xmax) < TOL, \
            f"X symmetry: xmin={bb.xmin:.3f}, xmax={bb.xmax:.3f}"
    
        # Check a point clearly inside the right page is inside the solid
        mid_x = (page_width / 2) * sa + (page_thickness / 2) * ca
        mid_z = (page_width / 2) * ca - (page_thickness / 2) * sa
        inside_pt_right = (mid_x, book_depth / 2, mid_z)
        assert result.val().isInside(inside_pt_right), \
            f"Point inside right page {inside_pt_right} should be inside the solid"
    
        # Check a point clearly inside the left page is inside the solid
        inside_pt_left = (-mid_x, book_depth / 2, mid_z)
        assert result.val().isInside(inside_pt_left), \
            f"Point inside left page {inside_pt_left} should be inside the solid"
    
        # Check a point in the open space between the pages is outside
        outside_pt = (0.0, book_depth / 2, page_width * ca / 2)
        assert not result.val().isInside(outside_pt), \
            f"Point in open V-space {outside_pt} should be outside the solid"
    
        # Check a point far above is outside
        far_outside = (0.0, book_depth / 2, page_width * 2)
        assert not result.val().isInside(far_outside), \
            f"Point far above {far_outside} should be outside the solid"
    
        # Volume cross-check via bounding box (volume should be much less than bbox volume)
        bbox_vol = bb.xlen * bb.ylen * bb.zlen
        fill_ratio = actual_vol / bbox_vol
        assert fill_ratio < 0.15, \
            f"Fill ratio too high ({fill_ratio:.3f}): pages should be thin strips, not filling the bounding box"
    
        print(f"All assertions passed!")
        print(f"Bounding box: X={bb.xlen:.2f}, Y={bb.ylen:.2f}, Z={bb.zlen:.2f}")
        print(f"Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
        print(f"Fill ratio: {fill_ratio:.4f}")
        print(f"Face count: {result.faces().size()}")
        print(f"Solid count: {result.solids().size()}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00681053/gpt_generated.stl')
