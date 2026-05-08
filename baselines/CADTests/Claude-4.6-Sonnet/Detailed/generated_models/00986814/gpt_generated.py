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
        rect_length = 0.25   # X direction
        rect_width  = 0.75   # Y direction
        rect_height = 0.02   # Z direction
    
        cyl_diameter = 0.07
        cyl_radius   = cyl_diameter / 2.0   # 0.035
        cyl_height   = 0.04
    
        # --- Step 1: Create the base rectangle (box) ---
        # Centered at origin: X in [-0.125, 0.125], Y in [-0.375, 0.375], Z in [0, 0.02]
        base = cq.Workplane("XY").box(rect_length, rect_width, rect_height,
                                       centered=(True, True, False))
    
        # --- Step 2: Place two cylinders on one end (the +X end) ---
        # Cylinders sit on top of the rectangle (z = rect_height = 0.02)
        # Centers in X: near the +X end, x = rect_length/2 - cyl_radius = 0.125 - 0.035 = 0.09
        # Centers in Y: side by side, touching: y = -cyl_radius and y = +cyl_radius
        cyl_x = rect_length / 2.0 - cyl_radius   # 0.09
        cyl_y1 = -cyl_radius                      # -0.035
        cyl_y2 = +cyl_radius                      # +0.035
    
        # Add cylinder 1
        cyl1 = cq.Workplane("XY").workplane(offset=rect_height).center(cyl_x, cyl_y1).circle(cyl_radius).extrude(cyl_height)
    
        # Add cylinder 2
        cyl2 = cq.Workplane("XY").workplane(offset=rect_height).center(cyl_x, cyl_y2).circle(cyl_radius).extrude(cyl_height)
    
        # --- Step 3: Union all parts ---
        result = base.union(cyl1).union(cyl2)
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X: from -0.125 to 0.125 (base) → xlen = 0.25
        assert abs(bb.xlen - rect_length) < TOL, f"X length: expected {rect_length}, got {bb.xlen}"
    
        # Y: from -0.375 to 0.375 (base) → ylen = 0.75
        assert abs(bb.ylen - rect_width) < TOL, f"Y width: expected {rect_width}, got {bb.ylen}"
    
        # Z: from 0 to rect_height + cyl_height = 0.02 + 0.04 = 0.06
        expected_zlen = rect_height + cyl_height
        assert abs(bb.zlen - expected_zlen) < TOL, f"Z height: expected {expected_zlen}, got {bb.zlen}"
    
        # Z min should be 0 (base starts at z=0)
        assert abs(bb.zmin - 0.0) < TOL, f"Z min: expected 0.0, got {bb.zmin}"
    
        # Z max should be 0.06
        assert abs(bb.zmax - expected_zlen) < TOL, f"Z max: expected {expected_zlen}, got {bb.zmax}"
    
        # Volume check
        base_vol = rect_length * rect_width * rect_height
        cyl_vol  = math.pi * cyl_radius**2 * cyl_height
        expected_vol = base_vol + 2 * cyl_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Cylindrical faces: 2 cylinders, OCCT splits each cylinder lateral face at seam
        # → 2 cylindrical face segments per cylinder → 4 total
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 4, f"Cylindrical faces: expected 4, got {cyl_faces}"
    
        # Circular edges on top faces of cylinders:
        # OCCT splits each circle into 2 arcs at the seam → 2 cylinders × 2 arcs = 4
        top_circular_edges = result.faces(">Z").edges("%Circle").size()
        assert top_circular_edges == 4, \
            f"Top circular edges: expected 4, got {top_circular_edges}"
    
        # Check that cylinders are on top of the base (z starts at rect_height)
        # A point inside cylinder 1 should be inside the solid
        cyl1_center_point = (cyl_x, cyl_y1, rect_height + cyl_height / 2.0)
        assert result.val().isInside(cyl1_center_point), \
            f"Point inside cylinder 1 {cyl1_center_point} should be inside solid"
    
        cyl2_center_point = (cyl_x, cyl_y2, rect_height + cyl_height / 2.0)
        assert result.val().isInside(cyl2_center_point), \
            f"Point inside cylinder 2 {cyl2_center_point} should be inside solid"
    
        # Check base is present: a point in the middle of the base
        base_center_point = (0.0, 0.0, rect_height / 2.0)
        assert result.val().isInside(base_center_point), \
            f"Point inside base {base_center_point} should be inside solid"
    
        # Check that a point far from the solid is outside
        outside_point = (1.0, 1.0, 1.0)
        assert not result.val().isInside(outside_point), \
            f"Point {outside_point} should be outside solid"
    
        # Check points above the base but outside cylinders are outside the solid
        # Point above base center but above rect_height (no cylinder there)
        above_base_no_cyl = (0.0, 0.0, rect_height + cyl_height / 2.0)
        assert not result.val().isInside(above_base_no_cyl), \
            f"Point above base center (no cylinder) {above_base_no_cyl} should be outside solid"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.4f} x {bb.ylen:.4f} x {bb.zlen:.4f}")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"  Cylindrical faces: {cyl_faces}")
        print(f"  Top circular edges: {top_circular_edges}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00986814/gpt_generated.stl')
