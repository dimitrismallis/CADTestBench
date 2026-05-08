import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        base = 0.150756       # base length of isosceles triangle
        height = 1.5          # height of triangle
        extrude_h = 0.188445  # extrusion height
    
        half_base = base / 2.0  # 0.075378
    
        # --- Step 1: Sketch the isosceles triangle on XY plane ---
        # Vertices:
        #   Bottom-left:  (-half_base, 0)
        #   Bottom-right: ( half_base, 0)
        #   Top:          (0, height)
        # The triangle is drawn as a closed wire using lineTo + close()
    
        result = (
            cq.Workplane("XY")
            .moveTo(-half_base, 0)
            .lineTo(half_base, 0)
            .lineTo(0, height)
            .close()
            .extrude(extrude_h)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - base) < TOL, f"X length: expected {base}, got {bb.xlen}"
        assert abs(bb.ylen - height) < TOL, f"Y length: expected {height}, got {bb.ylen}"
        assert abs(bb.zlen - extrude_h) < TOL, f"Z length: expected {extrude_h}, got {bb.zlen}"
    
        # Bounding box position checks
        assert abs(bb.xmin - (-half_base)) < TOL, f"xmin: expected {-half_base}, got {bb.xmin}"
        assert abs(bb.xmax - half_base) < TOL, f"xmax: expected {half_base}, got {bb.xmax}"
        assert abs(bb.ymin - 0.0) < TOL, f"ymin: expected 0.0, got {bb.ymin}"
        assert abs(bb.ymax - height) < TOL, f"ymax: expected {height}, got {bb.ymax}"
        assert abs(bb.zmin - 0.0) < TOL, f"zmin: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - extrude_h) < TOL, f"zmax: expected {extrude_h}, got {bb.zmax}"
    
        # Volume check: triangle area * extrusion height
        triangle_area = 0.5 * base * height
        expected_volume = triangle_area * extrude_h
        actual_volume = solid.Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.001, \
            f"Volume: expected {expected_volume:.6f}, got {actual_volume:.6f}"
    
        # Face count: triangular prism has 5 faces
        # 2 triangular faces (top and bottom) + 3 rectangular side faces
        face_count = result.faces().size()
        assert face_count == 5, f"Face count: expected 5, got {face_count}"
    
        # Edge count: triangular prism has 9 edges
        edge_count = result.edges().size()
        assert edge_count == 9, f"Edge count: expected 9, got {edge_count}"
    
        # Vertex count: triangular prism has 6 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 6, f"Vertex count: expected 6, got {vertex_count}"
    
        # All faces should be planar (no cylindrical faces)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 5, f"Planar face count: expected 5, got {planar_face_count}"
    
        # Check symmetry: center of mass should be at x=0 (symmetric about YZ plane)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y - height / 3.0) < TOL, f"Center of mass Y: expected {height/3.0}, got {com.y}"
        assert abs(com.z - extrude_h / 2.0) < TOL, f"Center of mass Z: expected {extrude_h/2.0}, got {com.z}"
    
        # Check base angles are close to 90 degrees
        base_angle = math.degrees(math.atan2(height, half_base))
        assert base_angle > 85.0, f"Base angle should be close to 90°, got {base_angle:.2f}°"
    
        print(f"All assertions passed!")
        print(f"Base: {base}, Height: {height}, Extrusion: {extrude_h}")
        print(f"Triangle area: {triangle_area:.6f}")
        print(f"Volume: {actual_volume:.6f} (expected {expected_volume:.6f})")
        print(f"Base angles: {base_angle:.2f}°")
        print(f"Faces: {face_count}, Edges: {edge_count}, Vertices: {vertex_count}")
        print(f"Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00670466/gpt_generated.stl')
