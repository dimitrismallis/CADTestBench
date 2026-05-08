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
        base_width = 20.0      # base of the isosceles triangle
        height = 100.0         # height of the triangle (long dimension)
        extrude_depth = 10.0   # extrusion depth
    
        # Triangle vertices:
        # Bottom-left: (-base_width/2, 0)
        # Bottom-right: (base_width/2, 0)
        # Apex: (0, height)
    
        half_base = base_width / 2.0
    
        # --- Step 1: Create the isosceles triangle profile on XY plane ---
        triangle = (
            cq.Workplane("XY")
            .moveTo(-half_base, 0)
            .lineTo(half_base, 0)
            .lineTo(0, height)
            .close()
        )
    
        # --- Step 2: Extrude the triangle profile along Z axis ---
        result = triangle.extrude(extrude_depth)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Check bounding box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - base_width) < TOL, f"X length: expected {base_width}, got {bb.xlen}"
        assert abs(bb.ylen - height) < TOL, f"Y length: expected {height}, got {bb.ylen}"
        assert abs(bb.zlen - extrude_depth) < TOL, f"Z length: expected {extrude_depth}, got {bb.zlen}"
    
        # Check bounding box extents
        assert abs(bb.xmin - (-half_base)) < TOL, f"xmin: expected {-half_base}, got {bb.xmin}"
        assert abs(bb.xmax - half_base) < TOL, f"xmax: expected {half_base}, got {bb.xmax}"
        assert abs(bb.ymin - 0) < TOL, f"ymin: expected 0, got {bb.ymin}"
        assert abs(bb.ymax - height) < TOL, f"ymax: expected {height}, got {bb.ymax}"
        assert abs(bb.zmin - 0) < TOL, f"zmin: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - extrude_depth) < TOL, f"zmax: expected {extrude_depth}, got {bb.zmax}"
    
        # Check volume: triangle area * extrude_depth
        triangle_area = 0.5 * base_width * height
        expected_volume = triangle_area * extrude_depth
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.001, \
            f"Volume: expected {expected_volume}, got {actual_volume}"
    
        # Check face count: a triangular prism has 5 faces
        # (2 triangular end caps + 3 rectangular side faces)
        face_count = result.faces().size()
        assert face_count == 5, f"Face count: expected 5, got {face_count}"
    
        # Check planar faces: all 5 faces of a triangular prism are planar
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 5, f"Planar face count: expected 5, got {planar_face_count}"
    
        # Check edge count: a triangular prism has 9 edges
        edge_count = result.edges().size()
        assert edge_count == 9, f"Edge count: expected 9, got {edge_count}"
    
        # Check vertex count: a triangular prism has 6 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 6, f"Vertex count: expected 6, got {vertex_count}"
    
        # Check the two triangular faces (top and bottom, parallel to XY plane)
        top_bottom_faces = result.faces("|Z").size()
        assert top_bottom_faces == 2, f"Top/bottom triangular faces: expected 2, got {top_bottom_faces}"
    
        # Check center of mass (should be at centroid of triangle, mid-depth)
        # Centroid of triangle: x = 0 (symmetric), y = height/3
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x - 0) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y - height / 3.0) < TOL, f"Center of mass Y: expected {height/3.0}, got {com.y}"
        assert abs(com.z - extrude_depth / 2.0) < TOL, f"Center of mass Z: expected {extrude_depth/2.0}, got {com.z}"
    
        # Verify a point inside the solid (near centroid)
        inside_point = (0, height / 3.0, extrude_depth / 2.0)
        assert result.val().isInside(inside_point), \
            f"Point {inside_point} should be inside the solid"
    
        # Verify a point outside the solid (beyond apex)
        outside_point = (0, height + 1.0, extrude_depth / 2.0)
        assert not result.val().isInside(outside_point), \
            f"Point {outside_point} should be outside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00520453/gpt_generated.stl')
