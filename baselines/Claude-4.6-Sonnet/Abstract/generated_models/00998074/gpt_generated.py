import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        bulb_radius   = 10.0      # circle (bulb) radius
        stem_width    = 6.0       # rectangle width (~half bulb diameter)
        stem_height   = 42.0      # rectangle height (~7x width)
        extrude_depth = 3.0       # small extrusion depth
        hole_radius   = 1.5       # small hole radius
        overlap       = 2.0       # how much the rectangle overlaps into the circle
    
        # The rectangle is centered at x=0.
        # Bottom of rectangle at y = bulb_radius - overlap (slightly inside circle)
        # so the two shapes merge into one connected region.
        # Top of rectangle at y = (bulb_radius - overlap) + stem_height
        stem_bottom_y = bulb_radius - overlap                    # = 8
        stem_top_y    = stem_bottom_y + stem_height              # = 50
        stem_cy       = stem_bottom_y + stem_height / 2.0        # = 8 + 21 = 29
    
        # Hole center near top of rectangle (5mm from top)
        hole_cy = stem_top_y - 5.0   # = 45
        hole_cx = 0.0
    
        # --- Build the 2D sketch ---
        s = (
            cq.Sketch()
            # Bulb: circle centered at origin
            .circle(bulb_radius, mode="a")
            # Stem: rectangle overlapping slightly into the circle so they merge
            .push([(0.0, stem_cy)])
            .rect(stem_width, stem_height, mode="a")
            # Small hole near top of stem
            .push([(hole_cx, hole_cy)])
            .circle(hole_radius, mode="s")
        )
    
        # --- Extrude the sketch ---
        result = cq.Workplane("XY").placeSketch(s).extrude(extrude_depth)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # 1. Check there is exactly one solid (overlap ensures merge)
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # 2. Bounding box checks
        bb = result.val().BoundingBox()
    
        # X extent: dominated by bulb diameter = 2*bulb_radius = 20
        expected_xlen = 2 * bulb_radius
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X extent: expected {expected_xlen}, got {bb.xlen}"
    
        # Y extent: from bottom of circle (-bulb_radius=−10) to top of rectangle (stem_top_y=50)
        expected_ymin = -bulb_radius   # -10
        expected_ymax = stem_top_y     # 50
        expected_ylen = expected_ymax - expected_ymin  # 60
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y extent: expected {expected_ylen}, got {bb.ylen}"
    
        # Z extent: extrusion depth
        assert abs(bb.zlen - extrude_depth) < TOL, \
            f"Z extent: expected {extrude_depth}, got {bb.zlen}"
    
        # 3. Z bounds
        assert abs(bb.zmin - 0.0) < TOL, f"Z min should be 0, got {bb.zmin}"
        assert abs(bb.zmax - extrude_depth) < TOL, \
            f"Z max should be {extrude_depth}, got {bb.zmax}"
    
        # 4. Volume check
        # Approximate: (circle_area + rect_area - overlap_rect_area - hole_area) * depth
        # The overlap region (stem_width x overlap) is counted twice in circle+rect, subtract once
        circle_area  = math.pi * bulb_radius**2
        rect_area    = stem_width * stem_height
        hole_area    = math.pi * hole_radius**2
        # The overlap strip (stem_width x overlap) is inside both circle and rect
        # Union area ≈ circle_area + rect_area - overlap_strip (approximate, ignoring arc curvature)
        overlap_strip = stem_width * overlap
        expected_vol = (circle_area + rect_area - overlap_strip - hole_area) * extrude_depth
        actual_vol   = result.val().Volume()
        # Allow 10% tolerance (overlap strip approximation ignores circle curvature)
        assert abs(actual_vol - expected_vol) / expected_vol < 0.10, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 5. Check the hole exists: point inside hole should NOT be inside solid
        solid = result.val()
        hole_point = (hole_cx, hole_cy, extrude_depth / 2.0)
        assert not solid.isInside(hole_point), \
            f"Point {hole_point} should be inside the hole (not inside solid)"
    
        # 6. Point in the stem should be inside solid
        stem_point = (0.0, stem_cy, extrude_depth / 2.0)
        assert solid.isInside(stem_point), \
            f"Point {stem_point} should be inside the stem"
    
        # 7. Point in the bulb should be inside solid
        bulb_point = (0.0, 0.0, extrude_depth / 2.0)
        assert solid.isInside(bulb_point), \
            f"Point {bulb_point} should be inside the bulb"
    
        # 8. Cylindrical faces: at least 2 (bulb outer + hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 2, \
            f"Expected at least 2 cylindrical faces (bulb + hole), got {cyl_faces}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"Volume: {actual_vol:.2f} (expected ~{expected_vol:.2f})")
        print(f"Cylindrical faces: {cyl_faces}")
        print(f"Solids: {result.solids().size()}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00998074/gpt_generated.stl')
