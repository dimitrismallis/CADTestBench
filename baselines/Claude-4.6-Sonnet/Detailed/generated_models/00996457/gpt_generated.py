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
        R_large = 0.489821
        R_small = 0.319623
        offset  = 0.260308
        cx      = offset / 2.0   # = 0.130154
        height  = 0.006808
    
        # --- Step 1: Build the 2D sketch ---
        # Union of two large circles, then subtract two small circles
        s = (
            cq.Sketch()
            # Large circle at (-cx, 0)
            .push([(-cx, 0)])
            .circle(R_large, mode="a")
            # Large circle at (+cx, 0)
            .push([(+cx, 0)])
            .circle(R_large, mode="a")
            # Small circle cutout at (-cx, 0)
            .push([(-cx, 0)])
            .circle(R_small, mode="s")
            # Small circle cutout at (+cx, 0)
            .push([(+cx, 0)])
            .circle(R_small, mode="s")
        )
    
        # --- Step 2: Extrude the sketch ---
        result = cq.Workplane("XY").placeSketch(s).extrude(height)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X extent: the two large circles span from -cx - R_large to +cx + R_large
        expected_xlen = 2 * (cx + R_large)  # = 2 * (0.130154 + 0.489821) = 2 * 0.619975 = 1.23995
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen:.6f}, got {bb.xlen:.6f}"
    
        # Y extent: each large circle has radius R_large, centered at y=0
        expected_ylen = 2 * R_large  # = 2 * 0.489821 = 0.979642
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen:.6f}, got {bb.ylen:.6f}"
    
        # Z extent: height of extrusion
        assert abs(bb.zlen - height) < TOL, \
            f"Z length (height): expected {height:.6f}, got {bb.zlen:.6f}"
    
        # Z bounds
        assert abs(bb.zmin) < TOL, f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - height) < TOL, f"Z max: expected {height}, got {bb.zmax}"
    
        # Volume check:
        # Area of union of two circles - area of union of two small circles
        # Area of union of two circles with radius r, center distance d:
        # A_union = 2*r^2*arccos(d/(2r)) - (d/2)*sqrt(4r^2 - d^2) ... wait, that's intersection
        # A_union = 2*pi*r^2 - A_intersection
        # A_intersection = 2*r^2*arccos(d/(2r)) - (d/2)*sqrt(4r^2 - d^2)
        def circle_union_area(r, d):
            if d >= 2 * r:
                return 2 * math.pi * r**2
            # intersection area of two circles radius r, center distance d
            a_intersect = 2 * r**2 * math.acos(d / (2 * r)) - (d / 2) * math.sqrt(4 * r**2 - d**2)
            return 2 * math.pi * r**2 - a_intersect
    
        d = offset  # distance between centers = 0.260308
        A_large = circle_union_area(R_large, d)
        A_small = circle_union_area(R_small, d)
        A_net   = A_large - A_small
        expected_vol = A_net * height
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.8f}, got {actual_vol:.8f}"
    
        # Check that the shape has cylindrical faces (from the circles)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 2, \
            f"Expected at least 2 cylindrical faces (outer arcs), got {cyl_faces}"
    
        # Check the solid is a single solid
        n_solids = result.solids().size()
        assert n_solids == 1, f"Expected 1 solid, got {n_solids}"
    
        # Check interior holes exist: a point inside a small circle region should be outside the solid
        # The center of the left small circle is at (-cx, 0, height/2)
        # Since R_small < R_large, the center of the small circle is inside the large circle
        # After subtraction, the center of the small circle should be OUTSIDE the solid
        solid_shape = result.val()
        interior_hole_pt = cq.Vector(-cx, 0, height / 2)
        assert not solid_shape.isInside(interior_hole_pt), \
            f"Point at center of small circle should be outside (hole), but is inside"
    
        # A point in the annular region (between small and large circle) should be inside
        # Pick a point at radius (R_small + R_large)/2 from left center, along +y
        r_mid = (R_small + R_large) / 2.0
        annular_pt = cq.Vector(-cx, r_mid, height / 2)
        assert solid_shape.isInside(annular_pt), \
            f"Point in annular region should be inside solid, but is outside"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.6f} x {bb.ylen:.6f} x {bb.zlen:.6f}")
        print(f"  Volume: {actual_vol:.8f} (expected {expected_vol:.8f})")
        print(f"  Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00996457/gpt_generated.stl')
