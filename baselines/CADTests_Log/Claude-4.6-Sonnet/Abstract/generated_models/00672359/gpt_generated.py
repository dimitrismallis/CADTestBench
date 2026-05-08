import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        L = 20.0       # side length of the square (and triangle legs)
        depth = 3.0    # extrusion depth
    
        # --- Step 1: Define the combined polygon vertices ---
        # Square: (0,0) -> (L,0) -> (L,L) -> (0,L)
        # Triangle on top: right angle at (0,L), legs go to (L,L) [shared] and (0,2L)
        # Combined polygon (going around): (0,0) -> (L,0) -> (L,L) -> (0,2L) -> back to (0,0)
        # This is a quadrilateral (irregular rhombus shape)
    
        vertices = [
            (0, 0),
            (L, 0),
            (L, L),
            (0, 2 * L),
        ]
    
        # --- Step 2: Build the profile as a closed wire using lineTo ---
        result = (
            cq.Workplane("XY")
            .moveTo(vertices[0][0], vertices[0][1])
            .lineTo(vertices[1][0], vertices[1][1])
            .lineTo(vertices[2][0], vertices[2][1])
            .lineTo(vertices[3][0], vertices[3][1])
            .close()
            .extrude(depth)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xmin - 0) < TOL, f"xmin expected 0, got {bb.xmin}"
        assert abs(bb.xmax - L) < TOL, f"xmax expected {L}, got {bb.xmax}"
        assert abs(bb.ymin - 0) < TOL, f"ymin expected 0, got {bb.ymin}"
        assert abs(bb.ymax - 2 * L) < TOL, f"ymax expected {2*L}, got {bb.ymax}"
        assert abs(bb.zmin - 0) < TOL, f"zmin expected 0, got {bb.zmin}"
        assert abs(bb.zmax - depth) < TOL, f"zmax expected {depth}, got {bb.zmax}"
        assert abs(bb.xlen - L) < TOL, f"xlen expected {L}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * L) < TOL, f"ylen expected {2*L}, got {bb.ylen}"
        assert abs(bb.zlen - depth) < TOL, f"zlen expected {depth}, got {bb.zlen}"
    
        # Volume check:
        # Area of polygon = area of square + area of triangle
        # Square area = L * L = 400
        # Triangle area = 0.5 * L * L = 200
        # Total area = 600
        # Volume = 600 * depth = 1800
        square_area = L * L
        triangle_area = 0.5 * L * L
        total_area = square_area + triangle_area
        expected_volume = total_area * depth
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.01, \
            f"Volume expected ~{expected_volume:.2f}, got {actual_volume:.2f}"
    
        # Face count: quadrilateral prism has 2 flat end faces + 4 side faces = 6 faces
        face_count = result.faces().size()
        assert face_count == 6, f"Expected 6 faces, got {face_count}"
    
        # Check planar faces only (all faces should be planar for this shape)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, f"Expected 6 planar faces, got {planar_count}"
    
        # Edge count: quadrilateral prism has 4 top + 4 bottom + 4 vertical = 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Expected 12 edges, got {edge_count}"
    
        # Vertex count: 4 top + 4 bottom = 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Expected 8 vertices, got {vertex_count}"
    
        # Check the shape contains a point inside the square region
        assert result.val().isInside((L / 2, L / 2, depth / 2)), \
            "Point inside square region should be inside the solid"
    
        # Check the shape contains a point inside the triangle region
        # Triangle: vertices (0,L), (L,L), (0,2L) — centroid at (L/3, 4L/3)
        assert result.val().isInside((L / 3, 4 * L / 3, depth / 2)), \
            "Point inside triangle region should be inside the solid"
    
        # Check a point outside the shape (top-right of triangle area) is NOT inside
        assert not result.val().isInside((L - 1, 2 * L - 1, depth / 2)), \
            "Point outside the shape (upper right) should not be inside the solid"
    
        print(f"All assertions passed!")
        print(f"Volume: {actual_volume:.2f} mm³ (expected {expected_volume:.2f} mm³)")
        print(f"Faces: {face_count}, Edges: {edge_count}, Vertices: {vertex_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00672359/gpt_generated.stl')
