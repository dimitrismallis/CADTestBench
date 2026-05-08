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
        base_angle_deg = 85.0          # base angles close to 90°
        base_half = 10.0               # half of base width → full base = 20mm
        extrude_depth = 10.0           # extrusion depth in mm
    
        # --- Step 1: Compute triangle geometry ---
        # Isosceles triangle with base angles = 85°
        # Height from base to apex
        height = base_half * math.tan(math.radians(base_angle_deg))
        # Vertices (in 2D, on XY plane):
        #   A = (-base_half, 0)
        #   B = ( base_half, 0)
        #   C = (0, height)   ← apex
        A = (-base_half, 0.0)
        B = ( base_half, 0.0)
        C = (0.0, height)
    
        # --- Step 2: Draw the isosceles triangle as a closed wire and extrude ---
        result = (
            cq.Workplane("XY")
            .moveTo(A[0], A[1])
            .lineTo(B[0], B[1])
            .lineTo(C[0], C[1])
            .close()
            .extrude(extrude_depth)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        full_base = 2 * base_half  # 20mm
        assert abs(bb.xlen - full_base) < TOL, \
            f"X extent (base): expected {full_base}, got {bb.xlen}"
        assert abs(bb.ylen - height) < TOL, \
            f"Y extent (height): expected {height:.4f}, got {bb.ylen:.4f}"
        assert abs(bb.zlen - extrude_depth) < TOL, \
            f"Z extent (depth): expected {extrude_depth}, got {bb.zlen}"
    
        # Volume check: triangle area * depth
        triangle_area = 0.5 * full_base * height
        expected_volume = triangle_area * extrude_depth
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.01, \
            f"Volume: expected {expected_volume:.2f}, got {actual_volume:.2f}"
    
        # Face count: a triangular prism has 5 faces
        # (2 triangular end caps + 3 rectangular side faces)
        face_count = result.faces().size()
        assert face_count == 5, \
            f"Face count: expected 5 (triangular prism), got {face_count}"
    
        # Edge count: a triangular prism has 9 edges
        edge_count = result.edges().size()
        assert edge_count == 9, \
            f"Edge count: expected 9, got {edge_count}"
    
        # Vertex count: a triangular prism has 6 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 6, \
            f"Vertex count: expected 6, got {vertex_count}"
    
        # Check that the two triangular faces (top and bottom) are planar
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 5, \
            f"Planar faces: expected 5 (all faces of prism are planar), got {planar_faces}"
    
        # Check base angles are close to 90° by verifying the height/half-base ratio
        computed_angle = math.degrees(math.atan2(height, base_half))
        assert abs(computed_angle - base_angle_deg) < 0.01, \
            f"Base angle: expected {base_angle_deg}°, got {computed_angle:.4f}°"
    
        # Symmetry: center of mass should be at x=0 (symmetric about YZ plane)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, \
            f"Center of mass X: expected 0 (symmetric), got {com.x:.4f}"
    
        # Center of mass Y should be at height/3 (centroid of triangle)
        expected_com_y = height / 3.0
        assert abs(com.y - expected_com_y) < TOL, \
            f"Center of mass Y: expected {expected_com_y:.4f}, got {com.y:.4f}"
    
        # Center of mass Z should be at half the extrusion depth
        expected_com_z = extrude_depth / 2.0
        assert abs(com.z - expected_com_z) < TOL, \
            f"Center of mass Z: expected {expected_com_z:.4f}, got {com.z:.4f}"
    
        print(f"✓ Triangular prism created successfully.")
        print(f"  Base angles: {base_angle_deg}° (close to 90°)")
        print(f"  Base width: {full_base} mm, Height: {height:.4f} mm, Depth: {extrude_depth} mm")
        print(f"  Volume: {actual_volume:.2f} mm³")
        print(f"  Faces: {face_count}, Edges: {edge_count}, Vertices: {vertex_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00670466/gpt_generated.stl')
