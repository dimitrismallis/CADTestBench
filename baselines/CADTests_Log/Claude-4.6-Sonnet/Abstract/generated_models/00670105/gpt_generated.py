import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        W = 60.0        # width of the rectangular base
        H_rect = 40.0   # height of the rectangular portion
        H_tri = 30.0    # height of the triangular roof portion
        depth = 50.0    # extrusion depth
    
        # --- Step 1: Define the 5 vertices of the pentagon (house shape) ---
        # Lower part is rectangular, upper part is triangular
        half_w = W / 2.0
        apex_y = H_rect + H_tri
    
        # Vertices in order (counter-clockwise):
        # bottom-left, bottom-right, top-right, apex, top-left
        pts = [
            (-half_w, 0),       # bottom-left
            ( half_w, 0),       # bottom-right
            ( half_w, H_rect),  # top-right of rectangle
            (0,       apex_y),  # apex of triangle
            (-half_w, H_rect),  # top-left of rectangle
        ]
    
        # --- Step 2: Build the 2D pentagon profile as a closed wire ---
        result = (
            cq.Workplane("XY")
            .moveTo(pts[0][0], pts[0][1])
            .lineTo(pts[1][0], pts[1][1])
            .lineTo(pts[2][0], pts[2][1])
            .lineTo(pts[3][0], pts[3][1])
            .lineTo(pts[4][0], pts[4][1])
            .close()
            # --- Step 3: Extrude to create the pentagonal prism ---
            .extrude(depth)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - W) < TOL, f"X length: expected {W}, got {bb.xlen}"
        assert abs(bb.ylen - (H_rect + H_tri)) < TOL, f"Y length: expected {H_rect + H_tri}, got {bb.ylen}"
        assert abs(bb.zlen - depth) < TOL, f"Z length (depth): expected {depth}, got {bb.zlen}"
    
        # Bounding box extents
        assert abs(bb.xmin - (-half_w)) < TOL, f"xmin: expected {-half_w}, got {bb.xmin}"
        assert abs(bb.xmax - half_w) < TOL, f"xmax: expected {half_w}, got {bb.xmax}"
        assert abs(bb.ymin - 0) < TOL, f"ymin: expected 0, got {bb.ymin}"
        assert abs(bb.ymax - apex_y) < TOL, f"ymax: expected {apex_y}, got {bb.ymax}"
        assert abs(bb.zmin - 0) < TOL, f"zmin: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - depth) < TOL, f"zmax: expected {depth}, got {bb.zmax}"
    
        # Face count: a pentagonal prism has 7 faces
        # (2 pentagonal end caps + 5 rectangular side faces)
        face_count = result.faces().size()
        assert face_count == 7, f"Face count: expected 7, got {face_count}"
    
        # Edge count: a pentagonal prism has 15 edges
        # (5 on each cap + 5 lateral edges)
        edge_count = result.edges().size()
        assert edge_count == 15, f"Edge count: expected 15, got {edge_count}"
    
        # Vertex count: a pentagonal prism has 10 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 10, f"Vertex count: expected 10, got {vertex_count}"
    
        # Volume check: area of pentagon cross-section * depth
        # Area of pentagon = area of rectangle + area of triangle
        rect_area = W * H_rect
        tri_area = 0.5 * W * H_tri
        penta_area = rect_area + tri_area
        expected_vol = penta_area * depth
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Planar faces: all 7 faces of a prism are planar
        planar_count = result.faces("%Plane").size()
        assert planar_count == 7, f"Planar faces: expected 7, got {planar_count}"
    
        # Check that the apex point is inside the solid
        apex_inside = solid.isInside((0, apex_y - 1, depth / 2))
        assert apex_inside, "Apex region should be inside the solid"
    
        # Check that a point outside the triangular roof is NOT inside
        outside_pt = solid.isInside((half_w - 1, apex_y - 1, depth / 2))
        assert not outside_pt, "Point outside the triangular roof should not be inside the solid"
    
        # Check symmetry: center of mass should be at x=0 (symmetric about YZ plane)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"Center of mass X should be 0 (symmetric), got {com.x}"
    
        # Center of mass Y: centroid of the pentagon cross-section
        # Centroid_y = (rect_area * H_rect/2 + tri_area * (H_rect + H_tri/3)) / penta_area
        centroid_y = (rect_area * (H_rect / 2) + tri_area * (H_rect + H_tri / 3)) / penta_area
        assert abs(com.y - centroid_y) < TOL, \
            f"Center of mass Y: expected {centroid_y:.4f}, got {com.y:.4f}"
    
        # Center of mass Z should be at depth/2
        assert abs(com.z - depth / 2) < TOL, \
            f"Center of mass Z: expected {depth/2}, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00670105/gpt_generated.stl')
