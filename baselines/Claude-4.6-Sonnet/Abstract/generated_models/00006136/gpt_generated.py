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
        base   = 40.0   # horizontal leg (along X)
        height = 30.0   # vertical leg (along Y)
        depth  = 20.0   # extrusion depth (along Z)
    
        # --- Step 1: Draw the right-triangle profile on the XY plane ---
        # Vertices: (0,0), (base,0), (0,height)
        # Right angle is at the origin.
        profile = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(base, 0)
            .lineTo(0, height)
            .close()
        )
    
        # --- Step 2: Extrude the triangle profile by `depth` in +Z ---
        result = profile.extrude(depth)
    
        # --- Final object verification ---
        TOL = 0.01
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - base)   < TOL, f"X length: expected {base}, got {bb.xlen}"
        assert abs(bb.ylen - height) < TOL, f"Y length: expected {height}, got {bb.ylen}"
        assert abs(bb.zlen - depth)  < TOL, f"Z length: expected {depth}, got {bb.zlen}"
    
        # Bounding box extents
        assert abs(bb.xmin - 0)      < TOL, f"xmin: expected 0, got {bb.xmin}"
        assert abs(bb.ymin - 0)      < TOL, f"ymin: expected 0, got {bb.ymin}"
        assert abs(bb.zmin - 0)      < TOL, f"zmin: expected 0, got {bb.zmin}"
        assert abs(bb.xmax - base)   < TOL, f"xmax: expected {base}, got {bb.xmax}"
        assert abs(bb.ymax - height) < TOL, f"ymax: expected {height}, got {bb.ymax}"
        assert abs(bb.zmax - depth)  < TOL, f"zmax: expected {depth}, got {bb.zmax}"
    
        # Volume: area of right triangle × depth = (0.5 * base * height) * depth
        expected_vol = 0.5 * base * height * depth
        actual_vol   = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count: a triangular prism has exactly 5 faces
        # (2 triangular end caps + 3 rectangular side faces)
        face_count = result.faces().size()
        assert face_count == 5, f"Face count: expected 5, got {face_count}"
    
        # Edge count: a triangular prism has exactly 9 edges
        edge_count = result.edges().size()
        assert edge_count == 9, f"Edge count: expected 9, got {edge_count}"
    
        # Vertex count: a triangular prism has exactly 6 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 6, f"Vertex count: expected 6, got {vertex_count}"
    
        # All faces should be planar (no curved surfaces)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 5, f"Planar faces: expected 5, got {planar_count}"
    
        # The two triangular faces (top and bottom) are perpendicular to Z
        z_faces = result.faces("|Z").size()
        assert z_faces == 2, f"Faces parallel to XY (|Z): expected 2, got {z_faces}"
    
        # Check that the right-angle corner point is inside the solid
        # (slightly inside from the corner at origin)
        inside_pt = (0.5, 0.5, depth / 2)
        assert solid.isInside(inside_pt), \
            f"Point {inside_pt} should be inside the solid"
    
        # Check that a point outside the triangle footprint is NOT inside
        outside_pt = (base * 0.6, height * 0.6, depth / 2)
        assert not solid.isInside(outside_pt), \
            f"Point {outside_pt} should be outside the solid"
    
        # Center of mass should be at (base/3, height/3, depth/2)
        # (centroid of a right triangle is at 1/3 of each leg from the right angle)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x - base   / 3) < TOL, f"CoM X: expected {base/3:.4f}, got {com.x:.4f}"
        assert abs(com.y - height / 3) < TOL, f"CoM Y: expected {height/3:.4f}, got {com.y:.4f}"
        assert abs(com.z - depth  / 2) < TOL, f"CoM Z: expected {depth/2:.4f}, got {com.z:.4f}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00006136/gpt_generated.stl')
