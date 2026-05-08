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
        w = 60.0        # full width
        h = 40.0        # full height
        cut = 10.0      # corner cut size (both x and y)
        thickness = 5.0 # extrusion thickness
    
        # Half dimensions
        hw = w / 2   # 30
        hh = h / 2   # 20
    
        # --- Step 1: Define the 6 vertices of the irregular hexagon ---
        # Starting from bottom-left, going clockwise:
        # 1. Bottom-left:  (-hw, -hh)
        # 2. Bottom-right: ( hw, -hh)
        # 3. Right side (before cut): ( hw,  hh - cut)  = (30, 10)
        # 4. Top-right (after cut):   ( hw - cut,  hh)  = (20, 20)
        # 5. Top-left (after cut):    (-hw + cut,  hh)  = (-20, 20)
        # 6. Left side (before cut):  (-hw,  hh - cut)  = (-30, 10)
    
        pts = [
            (-hw,       -hh),        # 1 bottom-left
            ( hw,       -hh),        # 2 bottom-right
            ( hw,        hh - cut),  # 3 lower-right
            ( hw - cut,  hh),        # 4 upper-right
            (-hw + cut,  hh),        # 5 upper-left
            (-hw,        hh - cut),  # 6 lower-left
        ]
    
        # --- Step 2: Build the hexagonal wire and extrude ---
        result = (
            cq.Workplane("XY")
            .moveTo(pts[0][0], pts[0][1])
            .lineTo(pts[1][0], pts[1][1])
            .lineTo(pts[2][0], pts[2][1])
            .lineTo(pts[3][0], pts[3][1])
            .lineTo(pts[4][0], pts[4][1])
            .lineTo(pts[5][0], pts[5][1])
            .close()
            .extrude(thickness)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - w) < TOL, f"X length: expected {w}, got {bb.xlen}"
        assert abs(bb.ylen - h) < TOL, f"Y length: expected {h}, got {bb.ylen}"
        assert abs(bb.zlen - thickness) < TOL, f"Z length: expected {thickness}, got {bb.zlen}"
    
        # Bounding box extents
        assert abs(bb.xmin - (-hw)) < TOL, f"xmin: expected {-hw}, got {bb.xmin}"
        assert abs(bb.xmax -  hw)   < TOL, f"xmax: expected {hw}, got {bb.xmax}"
        assert abs(bb.ymin - (-hh)) < TOL, f"ymin: expected {-hh}, got {bb.ymin}"
        assert abs(bb.ymax -  hh)   < TOL, f"ymax: expected {hh}, got {bb.ymax}"
        assert abs(bb.zmin - 0)     < TOL, f"zmin: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - thickness) < TOL, f"zmax: expected {thickness}, got {bb.zmax}"
    
        # Volume: rectangle area minus two corner triangles, times thickness
        rect_area = w * h                          # 60 * 40 = 2400
        corner_area = 2 * 0.5 * cut * cut         # 2 * 0.5 * 10 * 10 = 100
        expected_area = rect_area - corner_area    # 2300
        expected_vol = expected_area * thickness   # 2300 * 5 = 11500
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) < 1.0, \
            f"Volume: expected {expected_vol}, got {actual_vol:.3f}"
    
        # Face count: 2 hexagonal faces (top + bottom) + 6 side faces = 8 total
        face_count = result.faces().size()
        assert face_count == 8, f"Face count: expected 8, got {face_count}"
    
        # All faces should be planar (no cylinders)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 8, f"Planar face count: expected 8, got {planar_count}"
    
        # Top and bottom faces (parallel to XY plane)
        horiz_faces = result.faces("|Z").size()
        assert horiz_faces == 2, f"Horizontal faces: expected 2, got {horiz_faces}"
    
        # Vertex count: 6 vertices on top + 6 on bottom = 12
        vertex_count = result.vertices().size()
        assert vertex_count == 12, f"Vertex count: expected 12, got {vertex_count}"
    
        # Edge count: 6 top + 6 bottom + 6 vertical = 18
        edge_count = result.edges().size()
        assert edge_count == 18, f"Edge count: expected 18, got {edge_count}"
    
        # Center of mass should be at (0, 0, thickness/2) — symmetric in X
        # Y center: slightly below 0 due to cut corners at top
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected ~0, got {com.x}"
        assert abs(com.z - thickness / 2) < TOL, f"CoM Z: expected {thickness/2}, got {com.z}"
    
        # The top face should be at z = thickness
        top_z = result.faces(">Z").val().Center().z
        assert abs(top_z - thickness) < TOL, f"Top face Z: expected {thickness}, got {top_z}"
    
        # The bottom face should be at z = 0
        bot_z = result.faces("<Z").val().Center().z
        assert abs(bot_z - 0) < TOL, f"Bottom face Z: expected 0, got {bot_z}"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"  Volume: {actual_vol:.2f} (expected {expected_vol})")
        print(f"  Faces: {face_count}, Vertices: {vertex_count}, Edges: {edge_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00681547/gpt_generated.stl')
