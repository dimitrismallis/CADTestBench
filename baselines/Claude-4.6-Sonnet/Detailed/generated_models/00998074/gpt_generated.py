import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    from scipy import integrate
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        circle_diameter = 0.358436
        circle_radius = circle_diameter / 2  # 0.179218
    
        rect_length = 0.192347   # width in X
        rect_width = 0.592709    # height in Y (the "width" of the stem)
        extrude_depth = 0.029536
    
        overlap = 0.02193        # how much rect bottom overlaps into circle
    
        hole_diameter = 0.052367
        hole_radius = hole_diameter / 2
        hole_from_top = 0.048552  # distance from top edge of rectangle
    
        # --- Geometry calculations ---
        rect_bottom_y = -(circle_radius - overlap)  # = -0.157288
        rect_top_y = rect_bottom_y + rect_width      # = 0.435421
        rect_center_y = (rect_bottom_y + rect_top_y) / 2
    
        # Small hole position
        hole_y = rect_top_y - hole_from_top  # = 0.386869
        hole_x = 0.0
    
        # --- Step 1: Create the bulb circle face ---
        # --- Step 2: Create the stem rectangle face ---
        # --- Step 3: Union them, subtract hole, extrude ---
    
        sketch = (
            cq.Sketch()
            .circle(circle_radius)
            .push([(0, rect_center_y)])
            .rect(rect_length, rect_width)
            .push([(hole_x, hole_y)])
            .circle(hole_radius, mode="s")
            .reset()
        )
    
        result = cq.Workplane("XY").placeSketch(sketch).extrude(extrude_depth)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Check bounding box
        bb = result.val().BoundingBox()
    
        # X extent: dominated by circle diameter
        expected_xlen = circle_diameter
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected ~{expected_xlen:.4f}, got {bb.xlen:.4f}"
    
        # Y extent
        expected_ymin = -circle_radius
        expected_ymax = rect_top_y
        expected_ylen = expected_ymax - expected_ymin
        assert abs(bb.ymin - expected_ymin) < TOL, \
            f"Y min: expected ~{expected_ymin:.4f}, got {bb.ymin:.4f}"
        assert abs(bb.ymax - expected_ymax) < TOL, \
            f"Y max: expected ~{expected_ymax:.4f}, got {bb.ymax:.4f}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected ~{expected_ylen:.4f}, got {bb.ylen:.4f}"
    
        # Z extent: extrusion depth
        assert abs(bb.zlen - extrude_depth) < TOL, \
            f"Z length (extrusion depth): expected {extrude_depth:.6f}, got {bb.zlen:.6f}"
    
        # --- Volume check using numerical integration ---
        # Union area = circle_area + rect_area - intersection_area - hole_area
        # Intersection: circle ∩ rectangle
        # Rectangle x in [-rect_length/2, rect_length/2], y in [rect_bottom_y, rect_top_y]
        # Circle: x^2 + y^2 <= circle_radius^2
        # The intersection region: x in [-rect_length/2, rect_length/2],
        #   y in [max(rect_bottom_y, -sqrt(r^2-x^2)), min(rect_top_y, sqrt(r^2-x^2))]
        # Since rect_top_y > circle_radius, the upper bound is sqrt(r^2-x^2) for |x| <= r
        # and rect_bottom_y < -circle_radius is false (rect_bottom_y = -0.157288 > -0.179218)
        # so lower bound is rect_bottom_y for |x| <= sqrt(r^2 - rect_bottom_y^2)
        # and lower bound is -sqrt(r^2-x^2) for |x| > sqrt(r^2 - rect_bottom_y^2)
    
        r = circle_radius
        x_half = rect_length / 2  # 0.096174
        # x_half < r, so the rectangle is fully within the circle's x-extent
    
        def intersection_integrand(x):
            if abs(x) > r:
                return 0.0
            y_circle_top = math.sqrt(r**2 - x**2)
            y_circle_bot = -y_circle_top
            y_rect_bot = rect_bottom_y
            y_rect_top = rect_top_y
            y_low = max(y_circle_bot, y_rect_bot)
            y_high = min(y_circle_top, y_rect_top)
            if y_high <= y_low:
                return 0.0
            return y_high - y_low
    
        intersection_area, _ = integrate.quad(intersection_integrand, -x_half, x_half)
    
        circle_area = math.pi * r ** 2
        rect_area = rect_length * rect_width
        hole_area = math.pi * hole_radius ** 2
    
        # Union area = circle + rect - intersection - hole
        union_area = circle_area + rect_area - intersection_area - hole_area
        expected_vol = union_area * extrude_depth
    
        actual_vol = result.val().Volume()
        # Allow 5% tolerance
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical faces exist (circle bulb + hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 2, \
            f"Expected at least 2 cylindrical faces (bulb + hole), got {cyl_faces}"
    
        # Check the hole exists: point inside hole should NOT be inside solid
        hole_point_inside = (hole_x, hole_y, extrude_depth / 2)
        solid_shape = result.val()
        assert not solid_shape.isInside(hole_point_inside), \
            f"Point {hole_point_inside} should be inside the hole (not in solid), but it is inside"
    
        # Check a point in the bulb IS inside the solid
        bulb_point = (0.0, 0.0, extrude_depth / 2)
        assert solid_shape.isInside(bulb_point), \
            f"Point {bulb_point} should be inside the bulb, but it is not"
    
        # Check a point in the stem IS inside the solid
        stem_point = (0.0, rect_center_y, extrude_depth / 2)
        assert solid_shape.isInside(stem_point), \
            f"Point {stem_point} should be inside the stem, but it is not"
    
        print(f"All assertions passed!")
        print(f"Bounding box: X={bb.xlen:.4f}, Y={bb.ylen:.4f}, Z={bb.zlen:.6f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Cylindrical faces: {cyl_faces}")
        print(f"Intersection area: {intersection_area:.6f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00998074/gpt_generated.stl')
