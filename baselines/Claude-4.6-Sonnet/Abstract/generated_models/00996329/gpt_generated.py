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
        vertical_width  = 5.0   # width of the vertical leg (X direction)
        total_height    = 20.0  # total height of the L (Y direction)
        horizontal_len  = 15.0  # total length of the horizontal leg (X direction)
        horizontal_h    = 5.0   # height of the horizontal leg (Y direction)
        depth           = 5.0   # extrusion depth (Z direction)
    
        # --- Step 1: Sketch the L-shape profile in the XY plane ---
        # The L is drawn as a closed polygon with 6 vertices:
        #
        #  (0,20) ---- (5,20)
        #    |              |
        #    |              |
        #    |              |
        #  (0, 5) ---- (5, 5) ---- (15, 5)
        #    |                          |
        #  (0, 0) ---- (15, 0) ---------+
        #
        # We draw the outline starting from the bottom-left corner going clockwise.
    
        result = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(horizontal_len, 0)          # bottom edge (right)
            .lineTo(horizontal_len, horizontal_h)  # right side of horizontal leg (up)
            .lineTo(vertical_width, horizontal_h)  # top of horizontal leg (left)
            .lineTo(vertical_width, total_height)  # right side of vertical leg (up)
            .lineTo(0, total_height)            # top of vertical leg (left)
            .close()                            # back to (0,0)
            .extrude(depth)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box check
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - horizontal_len) < TOL, \
            f"X length: expected {horizontal_len}, got {bb.xlen}"
        assert abs(bb.ylen - total_height) < TOL, \
            f"Y length: expected {total_height}, got {bb.ylen}"
        assert abs(bb.zlen - depth) < TOL, \
            f"Z length: expected {depth}, got {bb.zlen}"
    
        # 2. Volume check
        # L-profile area = vertical leg area + horizontal extension area
        # vertical leg: vertical_width * total_height = 5 * 20 = 100
        # horizontal extension: (horizontal_len - vertical_width) * horizontal_h = 10 * 5 = 50
        l_area = (vertical_width * total_height) + \
                 ((horizontal_len - vertical_width) * horizontal_h)
        expected_vol = l_area * depth  # 150 * 5 = 750
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Face count check
        # An extruded L-shape (6-sided polygon) should have:
        # - 2 flat faces (top and bottom, the L-profile)
        # - 6 side faces (one per edge of the L outline)
        # Total = 8 faces
        face_count = result.faces().size()
        assert face_count == 8, \
            f"Face count: expected 8, got {face_count}"
    
        # 4. Edge count check
        # Each flat face has 6 edges, each side face has 4 edges
        # But edges are shared: 6 top + 6 bottom + 6 vertical side edges = 18 edges
        edge_count = result.edges().size()
        assert edge_count == 18, \
            f"Edge count: expected 18, got {edge_count}"
    
        # 5. Vertex count check
        # 6 vertices on top + 6 on bottom = 12 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 12, \
            f"Vertex count: expected 12, got {vertex_count}"
    
        # 6. Check that the solid is a single solid
        solid_count = result.solids().size()
        assert solid_count == 1, \
            f"Solid count: expected 1, got {solid_count}"
    
        # 7. Check top and bottom faces exist (parallel to XY plane)
        z_parallel_faces = result.faces("|Z").size()
        assert z_parallel_faces == 2, \
            f"Faces parallel to Z (top/bottom): expected 2, got {z_parallel_faces}"
    
        # 8. Check that a point inside the vertical leg is inside the solid
        inside_vertical = result.val().isInside((2.5, 15.0, 2.5))
        assert inside_vertical, \
            "Point (2.5, 15.0, 2.5) should be inside the vertical leg"
    
        # 9. Check that a point inside the horizontal leg is inside the solid
        inside_horizontal = result.val().isInside((10.0, 2.5, 2.5))
        assert inside_horizontal, \
            "Point (10.0, 2.5, 2.5) should be inside the horizontal leg"
    
        # 10. Check that a point in the missing corner (upper-right) is outside the solid
        outside_corner = result.val().isInside((10.0, 15.0, 2.5))
        assert not outside_corner, \
            "Point (10.0, 15.0, 2.5) should be OUTSIDE the L-bracket (missing corner)"
    
        # 11. Check bounding box origin (should start at 0,0,0)
        assert abs(bb.xmin - 0) < TOL, f"xmin: expected 0, got {bb.xmin}"
        assert abs(bb.ymin - 0) < TOL, f"ymin: expected 0, got {bb.ymin}"
        assert abs(bb.zmin - 0) < TOL, f"zmin: expected 0, got {bb.zmin}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00996329/gpt_generated.stl')
