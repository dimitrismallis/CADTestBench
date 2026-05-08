import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        base   = 0.3       # bottom length
        top    = 0.225     # top length
        height = 0.1875    # trapezoid height
        depth  = 0.75      # extrusion length
    
        # --- Step 1: Compute trapezoid vertices (centered at origin) ---
        # Centered: y goes from -height/2 to +height/2
        half_h  = height / 2.0   # 0.09375
        half_b  = base   / 2.0   # 0.15
        half_t  = top    / 2.0   # 0.1125
    
        # Vertices in CCW order:
        # Bottom-left, Bottom-right, Top-right, Top-left
        pts = [
            (-half_b, -half_h),   # bottom-left
            ( half_b, -half_h),   # bottom-right
            ( half_t,  half_h),   # top-right
            (-half_t,  half_h),   # top-left
        ]
    
        # --- Step 2: Build the trapezoid wire and extrude ---
        result = (
            cq.Workplane("XY")
            .moveTo(pts[0][0], pts[0][1])
            .lineTo(pts[1][0], pts[1][1])
            .lineTo(pts[2][0], pts[2][1])
            .lineTo(pts[3][0], pts[3][1])
            .close()
            .extrude(depth)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - base)   < TOL, f"X (base) expected {base}, got {bb.xlen}"
        assert abs(bb.ylen - height) < TOL, f"Y (height) expected {height}, got {bb.ylen}"
        assert abs(bb.zlen - depth)  < TOL, f"Z (depth) expected {depth}, got {bb.zlen}"
    
        # Bounding box extents (centered in X and Y, starting at Z=0)
        assert abs(bb.xmin - (-half_b)) < TOL, f"xmin expected {-half_b}, got {bb.xmin}"
        assert abs(bb.xmax -  half_b)   < TOL, f"xmax expected {half_b}, got {bb.xmax}"
        assert abs(bb.ymin - (-half_h)) < TOL, f"ymin expected {-half_h}, got {bb.ymin}"
        assert abs(bb.ymax -  half_h)   < TOL, f"ymax expected {half_h}, got {bb.ymax}"
        assert abs(bb.zmin - 0.0)       < TOL, f"zmin expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - depth)     < TOL, f"zmax expected {depth}, got {bb.zmax}"
    
        # Volume: trapezoid area * depth
        # Area of trapezoid = 0.5 * (base + top) * height
        trap_area = 0.5 * (base + top) * height
        expected_vol = trap_area * depth
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 1e-4, \
            f"Volume expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: a trapezoidal prism has 6 faces
        # (2 trapezoid end caps + 4 rectangular side faces)
        face_count = result.faces().size()
        assert face_count == 6, f"Face count expected 6, got {face_count}"
    
        # All faces should be planar
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, f"Planar face count expected 6, got {planar_count}"
    
        # Edge count: trapezoidal prism has 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count expected 12, got {edge_count}"
    
        # Vertex count: 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count expected 8, got {vertex_count}"
    
        # Center of mass should be at (0, 0, depth/2) for isosceles trapezoid
        # X centroid of isosceles trapezoid = 0 (symmetric)
        # Y centroid of trapezoid = h/3 * (2*top + base)/(top + base) - half_h
        # (using formula from bottom edge)
        # Centroid from bottom = h*(2*top + base) / (3*(top + base))
        y_centroid_from_bottom = height * (2*top + base) / (3*(top + base))
        y_centroid = y_centroid_from_bottom - half_h  # shift to centered coords
    
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x - 0.0)           < TOL, f"CoM X expected 0.0, got {com.x}"
        assert abs(com.y - y_centroid)     < TOL, f"CoM Y expected {y_centroid:.6f}, got {com.y:.6f}"
        assert abs(com.z - depth / 2.0)   < TOL, f"CoM Z expected {depth/2.0}, got {com.z}"
    
        # Check that a point inside the solid is correctly identified
        # A point at the centroid should be inside
        assert solid.isInside((0.0, y_centroid, depth / 2.0)), \
            "Centroid point should be inside the solid"
    
        # Check that a point outside (beyond the top edge) is not inside
        assert not solid.isInside((0.0, half_h + 0.01, depth / 2.0)), \
            "Point above top face should be outside the solid"
    
        print(f"All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.4f} x {bb.ylen:.4f} x {bb.zlen:.4f}")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"  Faces: {face_count}, Edges: {edge_count}, Vertices: {vertex_count}")
        print(f"  Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00998283/gpt_generated.stl')
