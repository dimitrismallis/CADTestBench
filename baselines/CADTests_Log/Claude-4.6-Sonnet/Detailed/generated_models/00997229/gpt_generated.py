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
        rect_length = 0.848067
        rect_width  = 0.197368
    
        # Circle diameters and radii
        d_small = 0.157782
        r_small = d_small / 2.0   # 0.078891
    
        d_large = 0.196626
        r_large = d_large / 2.0   # 0.098313
    
        # Hole diameters
        d_hole = 0.094737
        r_hole = d_hole / 2.0
    
        # Extrusion thickness
        thickness = 0.05
    
        # Centers of the two end circles along X axis
        # The rectangle spans from -rect_length/2 to +rect_length/2
        x_left  = -rect_length / 2.0   # center of small circle
        x_right = +rect_length / 2.0   # center of large circle
    
        half_w = rect_width / 2.0  # 0.098684
    
        # --- Step 1: Build the 2D wrench profile as a closed wire ---
        # The profile is the convex hull of:
        #   - Rectangle: from x_left to x_right, ±half_w in Y
        #   - Small circle at (x_left, 0) with radius r_small
        #   - Large circle at (x_right, 0) with radius r_large
        #
        # Since r_small (0.078891) < half_w (0.098684): small circle is inside rectangle width
        # Since r_large (0.098313) < half_w (0.098684): large circle is also inside rectangle width
        #
        # So the convex hull is just the rectangle with the circle ends "cutting in" at the ends.
        # Actually the profile should be: rectangle body + circular caps at each end.
        # The circles are centered at the rectangle ends. Since circles are smaller than rect width,
        # the profile is the rectangle with the end faces replaced by circular arcs (concave at ends).
        #
        # Better interpretation: The wrench head circles are the dominant feature at each end,
        # and the handle connects them. The overall outline is the convex hull.
        # 
        # Let me use a different approach: build the profile using the Sketch API
        # by creating a face that is the union of rectangle + two circles.
    
        # Use Sketch API with additive mode
        s = (
            cq.Sketch()
            .rect(rect_length, rect_width)
            .push([(x_left, 0)])
            .circle(r_small, mode="a")
            .reset()
            .push([(x_right, 0)])
            .circle(r_large, mode="a")
            .reset()
        )
    
        # --- Step 2: Extrude the profile ---
        result = cq.Workplane("XY").placeSketch(s).extrude(thickness)
    
        # --- Step 3: Cut holes in the two circular ends ---
        # Hole in small circle end (left, at x_left)
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints([(x_left, 0)])
            .hole(d_hole)
        )
    
        # Hole in large circle end (right, at x_right)
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints([(x_right, 0)])
            .hole(d_hole)
        )
    
        # --- Final object verification ---
        TOL = 0.005
    
        bb = result.val().BoundingBox()
    
        # Bounding box X: from x_left - r_small to x_right + r_large
        expected_xmin = x_left  - r_small
        expected_xmax = x_right + r_large
        expected_xlen = expected_xmax - expected_xmin
    
        # Bounding box Y: dominated by rectangle width (since circles are smaller)
        expected_ylen = rect_width  # rectangle is wider than both circles
    
        # Bounding box Z: thickness
        expected_zlen = thickness
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen:.6f}, got {bb.xlen:.6f}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen:.6f}, got {bb.ylen:.6f}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen:.6f}, got {bb.zlen:.6f}"
    
        # Volume check: approximate
        # Body volume ≈ (rect area + small circle area + large circle area) * thickness
        # But overlapping regions are counted once. Since circles are inside rect width,
        # the circles overlap with the rectangle at the ends.
        # Approximate: rect area + two semicircle caps (rough)
        # More precisely: union area = rect_area + circle_small_area + circle_large_area - overlaps
        # For a rough check, just verify it's positive and reasonable
        vol = result.val().Volume()
        rect_area = rect_length * rect_width
        # Rough lower bound: just the rectangle minus two holes
        hole_area = 2 * math.pi * r_hole**2
        lower_vol = (rect_area - hole_area) * thickness * 0.5  # very conservative
        assert vol > lower_vol, f"Volume too small: {vol:.6f} < {lower_vol:.6f}"
    
        # Check we have 2 cylindrical hole faces (the through-holes)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 2, f"Expected at least 2 cylindrical faces for holes, got {cyl_faces}"
    
        # Check the holes exist by verifying points inside the holes are NOT inside the solid
        solid = result.val()
        # Point at center of small hole, mid-thickness
        pt_small_hole = (x_left, 0, thickness / 2.0)
        assert not solid.isInside(pt_small_hole, tolerance=1e-4), \
            f"Small hole center should be outside solid, but isInside returned True"
    
        # Point at center of large hole, mid-thickness
        pt_large_hole = (x_right, 0, thickness / 2.0)
        assert not solid.isInside(pt_large_hole, tolerance=1e-4), \
            f"Large hole center should be outside solid, but isInside returned True"
    
        # Point in the middle of the handle should be inside
        pt_handle = (0, 0, thickness / 2.0)
        assert solid.isInside(pt_handle, tolerance=1e-4), \
            f"Handle center should be inside solid, but isInside returned False"
    
        # Check circular edges for holes (should have 4: top and bottom of each hole)
        circ_edges = result.edges("%Circle").size()
        assert circ_edges >= 4, f"Expected at least 4 circular edges (hole rims), got {circ_edges}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: X={bb.xlen:.6f}, Y={bb.ylen:.6f}, Z={bb.zlen:.6f}")
        print(f"Volume: {vol:.6f}")
        print(f"Cylindrical faces: {cyl_faces}")
        print(f"Circular edges: {circ_edges}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00997229/gpt_generated.stl')
