import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        circumradius = 10.0   # circumradius of hexagon (mm)
        height = 5.0          # extrusion height (mm)
        diameter = 2 * circumradius  # diameter for polygon() call
    
        # --- Step 1: Draw hexagon on XY plane and extrude ---
        result = (
            cq.Workplane("XY")
            .polygon(6, diameter)
            .extrude(height)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        # Flat-to-flat distance (apothem * 2) = sqrt(3) * circumradius
        flat_to_flat = math.sqrt(3) * circumradius  # ≈ 17.3205
        # Tip-to-tip distance = diameter = 20.0
        tip_to_tip = diameter  # 20.0
    
        assert abs(bb.xlen - tip_to_tip) < TOL, \
            f"BBox X (tip-to-tip): expected {tip_to_tip}, got {bb.xlen}"
        assert abs(bb.ylen - flat_to_flat) < TOL, \
            f"BBox Y (flat-to-flat): expected {flat_to_flat:.4f}, got {bb.ylen:.4f}"
        assert abs(bb.zlen - height) < TOL, \
            f"BBox Z (height): expected {height}, got {bb.zlen}"
    
        # Volume check: V = (3*sqrt(3)/2) * R^2 * h
        expected_volume = (3 * math.sqrt(3) / 2) * (circumradius ** 2) * height
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.001, \
            f"Volume: expected {expected_volume:.4f}, got {actual_volume:.4f}"
    
        # Face count: 6 side faces + 1 top + 1 bottom = 8
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
    
        # Top and bottom faces exist
        top_faces = result.faces(">Z").size()
        assert top_faces == 1, \
            f"Top face count: expected 1, got {top_faces}"
        bottom_faces = result.faces("<Z").size()
        assert bottom_faces == 1, \
            f"Bottom face count: expected 1, got {bottom_faces}"
    
        # All side faces are planar
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 8, \
            f"Planar face count: expected 8, got {planar_faces}"
    
        # Center of mass should be at origin (x=0, y=0, z=height/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - height / 2) < TOL, f"CoM Z: expected {height/2}, got {com.z}"
    
        # Check a point inside the solid
        assert result.val().isInside((0, 0, height / 2)), \
            "Center point should be inside the hexagonal prism"
    
        # Check a point outside the solid (beyond tip)
        assert not result.val().isInside((circumradius + 1, 0, height / 2)), \
            "Point beyond tip should be outside the hexagonal prism"
    
        print(f"Hexagonal prism created successfully!")
        print(f"  Circumradius: {circumradius} mm")
        print(f"  Height: {height} mm")
        print(f"  Volume: {actual_volume:.4f} mm³ (expected {expected_volume:.4f} mm³)")
        print(f"  Bounding box: {bb.xlen:.4f} x {bb.ylen:.4f} x {bb.zlen:.4f} mm")
        print(f"  Faces: {face_count}, Edges: {edge_count}, Vertices: {vertex_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00009823/gpt_generated.stl')
