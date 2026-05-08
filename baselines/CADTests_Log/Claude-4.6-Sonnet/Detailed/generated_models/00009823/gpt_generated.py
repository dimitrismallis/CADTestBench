import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        side_length = 1.5          # side length of hexagon
        height = 0.016238          # extrusion height
    
        # For a regular hexagon with side length s:
        # circumscribed circle diameter = 2 * s
        circumscribed_diameter = 2 * side_length  # = 3.0
    
        # --- Step 1: Create hexagonal profile and extrude ---
        result = (
            cq.Workplane("XY")
            .polygon(6, circumscribed_diameter)
            .extrude(height)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X extent: across corners = 2 * side_length = 3.0
        expected_x = 2 * side_length
        assert abs(bb.xlen - expected_x) < TOL, \
            f"X extent: expected {expected_x}, got {bb.xlen}"
    
        # Y extent: across flats = sqrt(3) * side_length
        expected_y = math.sqrt(3) * side_length
        assert abs(bb.ylen - expected_y) < TOL, \
            f"Y extent: expected {expected_y:.6f}, got {bb.ylen:.6f}"
    
        # Z extent: extrusion height
        assert abs(bb.zlen - height) < TOL, \
            f"Z extent: expected {height}, got {bb.zlen}"
    
        # Z bounds: bottom at 0, top at height
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - height) < TOL, \
            f"Z max: expected {height}, got {bb.zmax}"
    
        # Volume check
        hex_area = (3 * math.sqrt(3) / 2) * side_length ** 2
        expected_volume = hex_area * height
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 1e-4, \
            f"Volume: expected {expected_volume:.6f}, got {actual_volume:.6f}"
    
        # Face count: 2 hexagonal faces (top + bottom) + 6 rectangular side faces = 8
        face_count = result.faces().size()
        assert face_count == 8, \
            f"Face count: expected 8, got {face_count}"
    
        # Edge count: 6 top + 6 bottom + 6 vertical = 18
        edge_count = result.edges().size()
        assert edge_count == 18, \
            f"Edge count: expected 18, got {edge_count}"
    
        # Vertex count: 6 top + 6 bottom = 12
        vertex_count = result.vertices().size()
        assert vertex_count == 12, \
            f"Vertex count: expected 12, got {vertex_count}"
    
        # Top face (max Z) - 1 hexagonal face
        top_face_count = result.faces(">Z").size()
        assert top_face_count == 1, \
            f"Top face count: expected 1, got {top_face_count}"
    
        # Bottom face (min Z) - 1 hexagonal face
        bottom_face_count = result.faces("<Z").size()
        assert bottom_face_count == 1, \
            f"Bottom face count: expected 1, got {bottom_face_count}"
    
        # |Z selects faces whose normal is parallel to Z → top + bottom = 2 faces
        horiz_face_count = result.faces("|Z").size()
        assert horiz_face_count == 2, \
            f"Horizontal face count (|Z): expected 2, got {horiz_face_count}"
    
        # #Z selects faces whose normal is perpendicular to Z → 6 side faces
        side_face_count = result.faces("#Z").size()
        assert side_face_count == 6, \
            f"Side face count (#Z): expected 6, got {side_face_count}"
    
        # Center of mass should be at (0, 0, height/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - height / 2) < TOL, \
            f"CoM Z: expected {height/2}, got {com.z}"
    
        # Confirm a point at center mid-height is inside the solid
        mid_point = (0, 0, height / 2)
        assert result.val().isInside(mid_point), \
            "Center mid-height point should be inside the solid"
    
        # Confirm a point outside the hexagon is not inside
        outside_point = (side_length * 2, 0, height / 2)
        assert not result.val().isInside(outside_point), \
            "Point outside hexagon should not be inside the solid"
    
        print("All assertions passed!")
        print(f"  Side length: {side_length} units")
        print(f"  Height: {height} units")
        print(f"  Hex area: {hex_area:.6f} sq units")
        print(f"  Volume: {actual_volume:.6f} cubic units")
        print(f"  Bounding box: {bb.xlen:.4f} x {bb.ylen:.4f} x {bb.zlen:.6f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00009823/gpt_generated.stl')
