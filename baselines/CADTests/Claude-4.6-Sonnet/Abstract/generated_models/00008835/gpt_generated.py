import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        side_length = 50.0      # square side length (mm)
        extrude_height = 200.0  # extensive extrusion height (mm)
    
        # --- Step 1: Create a square profile on the XY plane ---
        square_profile = cq.Workplane("XY").rect(side_length, side_length)
    
        # --- Step 2: Perform an extensive extrusion ---
        result = square_profile.extrude(extrude_height)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Check bounding box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - side_length) < TOL, \
            f"X length: expected {side_length}, got {bb.xlen}"
        assert abs(bb.ylen - side_length) < TOL, \
            f"Y length: expected {side_length}, got {bb.ylen}"
        assert abs(bb.zlen - extrude_height) < TOL, \
            f"Z length (extrusion height): expected {extrude_height}, got {bb.zlen}"
    
        # Check bounding box position (centered in X and Y, starts at Z=0)
        assert abs(bb.xmin - (-side_length / 2)) < TOL, \
            f"X min: expected {-side_length/2}, got {bb.xmin}"
        assert abs(bb.xmax - (side_length / 2)) < TOL, \
            f"X max: expected {side_length/2}, got {bb.xmax}"
        assert abs(bb.ymin - (-side_length / 2)) < TOL, \
            f"Y min: expected {-side_length/2}, got {bb.ymin}"
        assert abs(bb.ymax - (side_length / 2)) < TOL, \
            f"Y max: expected {side_length/2}, got {bb.ymax}"
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - extrude_height) < TOL, \
            f"Z max: expected {extrude_height}, got {bb.zmax}"
    
        # Check volume: side^2 * height
        expected_volume = side_length * side_length * extrude_height
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) < TOL, \
            f"Volume: expected {expected_volume}, got {actual_volume}"
    
        # Check face count: a rectangular prism has 6 faces
        face_count = result.faces().size()
        assert face_count == 6, \
            f"Face count: expected 6, got {face_count}"
    
        # Check edge count: a rectangular prism has 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, \
            f"Edge count: expected 12, got {edge_count}"
    
        # Check vertex count: a rectangular prism has 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, \
            f"Vertex count: expected 8, got {vertex_count}"
    
        # Check that all faces are planar (no curved faces)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 6, \
            f"Planar face count: expected 6, got {planar_face_count}"
    
        # Check top face is at Z = extrude_height
        top_face_center = result.faces(">Z").val().Center()
        assert abs(top_face_center.z - extrude_height) < TOL, \
            f"Top face center Z: expected {extrude_height}, got {top_face_center.z}"
    
        # Check bottom face is at Z = 0
        bottom_face_center = result.faces("<Z").val().Center()
        assert abs(bottom_face_center.z - 0.0) < TOL, \
            f"Bottom face center Z: expected 0.0, got {bottom_face_center.z}"
    
        # Check center of mass is at the geometric center
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x - 0.0) < TOL, f"Center of mass X: expected 0.0, got {com.x}"
        assert abs(com.y - 0.0) < TOL, f"Center of mass Y: expected 0.0, got {com.y}"
        assert abs(com.z - extrude_height / 2) < TOL, \
            f"Center of mass Z: expected {extrude_height/2}, got {com.z}"
    
        # Check that 4 side faces are perpendicular to Z axis (normals lie in XY plane)
        # faces("#Z") selects faces whose normal is perpendicular to Z — these are the 4 side faces
        side_face_count = result.faces("#Z").size()
        assert side_face_count == 4, \
            f"Side faces (normals perpendicular to Z): expected 4, got {side_face_count}"
    
        # Check that 2 horizontal faces have normals parallel to Z (top and bottom)
        # faces("|Z") selects faces whose normal is parallel to Z
        horizontal_face_count = result.faces("|Z").size()
        assert horizontal_face_count == 2, \
            f"Horizontal faces (normals parallel to Z): expected 2, got {horizontal_face_count}"
    
        # Check that 4 vertical edges are parallel to Z axis
        vertical_edge_count = result.edges("|Z").size()
        assert vertical_edge_count == 4, \
            f"Vertical edges parallel to Z: expected 4, got {vertical_edge_count}"
    
        # Check that a point inside the solid is correctly identified
        interior_point = (0.0, 0.0, extrude_height / 2)
        assert result.val().isInside(interior_point), \
            f"Interior point {interior_point} should be inside the solid"
    
        # Check that a point outside the solid is correctly identified
        exterior_point = (side_length, side_length, extrude_height / 2)
        assert not result.val().isInside(exterior_point), \
            f"Exterior point {exterior_point} should be outside the solid"
    
        print("All assertions passed!")
        print(f"  Square side: {side_length} mm")
        print(f"  Extrusion height: {extrude_height} mm")
        print(f"  Volume: {actual_volume:.2f} mm³")
        print(f"  Faces: {face_count}, Edges: {edge_count}, Vertices: {vertex_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00008835/gpt_generated.stl')
