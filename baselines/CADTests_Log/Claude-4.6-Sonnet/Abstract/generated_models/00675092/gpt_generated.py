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
        leg_x = 40.0    # horizontal leg length
        leg_y = 30.0    # vertical leg length
        depth = 5.0     # marginal extrusion depth
    
        # --- Step 1: Draw the right triangle sketch on XY plane ---
        # Right angle at origin, legs along +X and +Y axes
        # Vertices: (0,0), (40,0), (0,30)
        result = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(leg_x, 0)
            .lineTo(0, leg_y)
            .close()
            .extrude(depth)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - leg_x) < TOL, f"X length: expected {leg_x}, got {bb.xlen}"
        assert abs(bb.ylen - leg_y) < TOL, f"Y length: expected {leg_y}, got {bb.ylen}"
        assert abs(bb.zlen - depth) < TOL, f"Z length (depth): expected {depth}, got {bb.zlen}"
    
        # Bounding box origin checks (triangle starts at origin)
        assert abs(bb.xmin - 0) < TOL, f"xmin: expected 0, got {bb.xmin}"
        assert abs(bb.ymin - 0) < TOL, f"ymin: expected 0, got {bb.ymin}"
        assert abs(bb.zmin - 0) < TOL, f"zmin: expected 0, got {bb.zmin}"
    
        # Volume: area of right triangle * depth = (0.5 * leg_x * leg_y) * depth
        expected_vol = 0.5 * leg_x * leg_y * depth
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count: a triangular prism has 5 faces
        # 2 triangular faces (top and bottom) + 3 rectangular side faces
        face_count = result.faces().size()
        assert face_count == 5, f"Face count: expected 5, got {face_count}"
    
        # Edge count: a triangular prism has 9 edges
        edge_count = result.edges().size()
        assert edge_count == 9, f"Edge count: expected 9, got {edge_count}"
    
        # Vertex count: a triangular prism has 6 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 6, f"Vertex count: expected 6, got {vertex_count}"
    
        # Check planar faces only (all 5 faces of a prism are planar)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 5, f"Planar face count: expected 5, got {planar_face_count}"
    
        # Check top and bottom faces exist (parallel to XY plane)
        z_parallel_faces = result.faces("|Z").size()
        assert z_parallel_faces == 2, f"Faces parallel to Z (top+bottom): expected 2, got {z_parallel_faces}"
    
        # Check the hypotenuse face (the slanted side face)
        # The hypotenuse connects (40,0) to (0,30), so there should be 3 side faces
        side_faces = result.faces("#Z").size()
        assert side_faces == 3, f"Side faces (perpendicular to Z): expected 3, got {side_faces}"
    
        # Center of mass should be at (leg_x/3, leg_y/3, depth/2) for a right triangle prism
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x - leg_x / 3) < TOL, f"CoM X: expected {leg_x/3:.4f}, got {com.x:.4f}"
        assert abs(com.y - leg_y / 3) < TOL, f"CoM Y: expected {leg_y/3:.4f}, got {com.y:.4f}"
        assert abs(com.z - depth / 2) < TOL, f"CoM Z: expected {depth/2:.4f}, got {com.z:.4f}"
    
        # Verify a point inside the solid is actually inside
        inside_pt = (leg_x / 4, leg_y / 4, depth / 2)
        assert solid.isInside(inside_pt), f"Point {inside_pt} should be inside the solid"
    
        # Verify a point outside the solid is not inside
        outside_pt = (leg_x, leg_y, depth / 2)  # corner of bounding box, outside triangle
        assert not solid.isInside(outside_pt), f"Point {outside_pt} should be outside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00675092/gpt_generated.stl')
