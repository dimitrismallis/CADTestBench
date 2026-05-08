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
        rect_width  = 0.477273   # length of the rectangular base
        rect_height = 0.2727275  # height of the rectangular part
        tri_base    = 0.204545   # base length of the triangular top part
        extrude_w   = 0.75       # extrusion depth (width of prism)
    
        # Triangle height: use a reasonable value.
        # The triangle is isoceles with base = tri_base.
        # We'll use the same proportion as the rectangle: height = rect_height
        tri_height  = rect_height  # 0.2727275
    
        # --- Step 1: Define the 5 vertices of the pentagon ---
        # The shape is centered horizontally.
        # Rectangle spans from -rect_width/2 to +rect_width/2 in X, 0 to rect_height in Y.
        # Triangle sits on top: base from -tri_base/2 to +tri_base/2 at Y=rect_height,
        # apex at (0, rect_height + tri_height).
    
        half_rw = rect_width / 2.0   # 0.238636
        half_tb = tri_base / 2.0     # 0.102273
    
        pts = [
            (-half_rw,  0.0),                        # bottom-left
            ( half_rw,  0.0),                        # bottom-right
            ( half_rw,  rect_height),                # upper-right of rectangle
            ( half_tb,  rect_height),                # right base of triangle
            ( 0.0,      rect_height + tri_height),   # apex
            (-half_tb,  rect_height),                # left base of triangle
            (-half_rw,  rect_height),                # upper-left of rectangle
        ]
        # Wait - this gives 7 vertices (heptagon), not 5.
        # A true pentagon has exactly 5 vertices.
        # Re-reading: "lower part is rectangular" and "top part is a triangle"
        # For a pentagon (5 sides, 5 vertices):
        # The rectangular part contributes 4 vertices (bottom 2 + top 2 of rectangle)
        # but the triangle shares the top edge of the rectangle as its base.
        # So: bottom-left, bottom-right, upper-right, apex, upper-left = 5 vertices
        # This means the triangle base = rect_width = 0.477273, not 0.204545.
        #
        # UNLESS: the "triangle base" refers to the slant sides meeting at a narrower top,
        # meaning the upper part tapers. In that case the 5 vertices are:
        # bottom-left, bottom-right, upper-right (narrower), apex, upper-left (narrower)
        # where upper-right = (half_tb, rect_height) and upper-left = (-half_tb, rect_height)
        # This gives a trapezoid bottom + triangle top = pentagon with 5 vertices? No, still 5.
        # Actually: bottom-left(-half_rw,0), bottom-right(half_rw,0),
        #           right-shoulder(half_tb, rect_height), apex(0, rect_height+tri_height),
        #           left-shoulder(-half_tb, rect_height) = 5 vertices! Yes!
        # The "rectangular" lower part is actually a trapezoid (wider at bottom, narrower at top)
        # but described as "rectangular" because it's the lower portion.
        # OR: the lower part IS a true rectangle, meaning the shape has more than 5 vertices.
        #
        # Given the constraint of exactly 5 vertices (pentagon), I'll use:
        # The shape tapers from rect_width at bottom to tri_base at the shoulder,
        # then comes to an apex. This gives exactly 5 vertices.
    
        pts5 = [
            (-half_rw,  0.0),                        # bottom-left
            ( half_rw,  0.0),                        # bottom-right
            ( half_tb,  rect_height),                # right shoulder
            ( 0.0,      rect_height + tri_height),   # apex
            (-half_tb,  rect_height),                # left shoulder
        ]
    
        # --- Step 2: Build the 2D profile using the Sketch API ---
        # Use lineTo to trace the pentagon outline
        profile = (
            cq.Workplane("XY")
            .moveTo(pts5[0][0], pts5[0][1])
            .lineTo(pts5[1][0], pts5[1][1])
            .lineTo(pts5[2][0], pts5[2][1])
            .lineTo(pts5[3][0], pts5[3][1])
            .lineTo(pts5[4][0], pts5[4][1])
            .close()
        )
    
        # --- Step 3: Extrude to create the pentagonal prism ---
        result = profile.extrude(extrude_w)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        expected_xlen = rect_width   # 0.477273
        expected_ylen = rect_height + tri_height  # 0.2727275 + 0.2727275 = 0.545455
        expected_zlen = extrude_w    # 0.75
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen}, got {bb.xlen}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen}, got {bb.ylen}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Volume check: pentagon area × extrude depth
        # Pentagon area = trapezoid area + triangle area
        # Trapezoid: parallel sides = rect_width (bottom) and tri_base (top), height = rect_height
        trap_area = 0.5 * (rect_width + tri_base) * rect_height
        # Triangle: base = tri_base, height = tri_height
        tri_area  = 0.5 * tri_base * tri_height
        pent_area = trap_area + tri_area
        expected_vol = pent_area * extrude_w
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: pentagonal prism has 7 faces (2 pentagons + 5 rectangles)
        face_count = result.faces().size()
        assert face_count == 7, \
            f"Face count: expected 7, got {face_count}"
    
        # Edge count: pentagonal prism has 15 edges (5 per pentagon × 2 + 5 lateral)
        edge_count = result.edges().size()
        assert edge_count == 15, \
            f"Edge count: expected 15, got {edge_count}"
    
        # Vertex count: 10 (5 per pentagon face)
        vertex_count = result.vertices().size()
        assert vertex_count == 10, \
            f"Vertex count: expected 10, got {vertex_count}"
    
        # Check the two pentagonal faces (front and back, perpendicular to Z)
        z_faces = result.faces("|Z").size()
        assert z_faces == 2, \
            f"Pentagonal faces (|Z): expected 2, got {z_faces}"
    
        # Check center of mass is at x=0 (symmetric about X), y = some positive value, z = extrude_w/2
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x - 0.0) < TOL, \
            f"Center of mass X: expected 0.0, got {com.x}"
        assert abs(com.z - extrude_w / 2.0) < TOL, \
            f"Center of mass Z: expected {extrude_w/2.0}, got {com.z}"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.6f} x {bb.ylen:.6f} x {bb.zlen:.6f}")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"  Faces: {face_count}, Edges: {edge_count}, Vertices: {vertex_count}")
        print(f"  Center of mass: ({com.x:.6f}, {com.y:.6f}, {com.z:.6f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00670105/gpt_generated.stl')
