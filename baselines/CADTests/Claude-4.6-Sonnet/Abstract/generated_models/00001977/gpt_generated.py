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
        side = 40.0
        extrude_height = 20.0
    
        # --- Step 1: Compute triangle vertices (equilateral, centered at origin) ---
        h = side * math.sqrt(3) / 2  # height of equilateral triangle ≈ 34.641
    
        # Centroid is at h/3 from base, 2h/3 from apex
        # Vertices centered so centroid is at (0, 0):
        v1 = (-side / 2, -h / 3)       # bottom-left
        v2 = ( side / 2, -h / 3)       # bottom-right
        v3 = (0,          2 * h / 3)   # top apex
    
        # --- Step 2: Draw the triangle profile and extrude ---
        result = (
            cq.Workplane("XY")
            .moveTo(v1[0], v1[1])
            .lineTo(v2[0], v2[1])
            .lineTo(v3[0], v3[1])
            .close()
            .extrude(extrude_height)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        expected_xlen = side  # 40.0
        expected_ylen = h     # ≈ 34.641
        expected_zlen = extrude_height  # 20.0
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen:.4f}, got {bb.xlen:.4f}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen:.4f}, got {bb.ylen:.4f}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen:.4f}, got {bb.zlen:.4f}"
    
        # Volume check: area of equilateral triangle * height
        triangle_area = (math.sqrt(3) / 4) * side ** 2  # ≈ 692.82
        expected_volume = triangle_area * extrude_height  # ≈ 13856.4
        assert abs(solid.Volume() - expected_volume) / expected_volume < 0.001, \
            f"Volume: expected ~{expected_volume:.2f}, got {solid.Volume():.2f}"
    
        # Face count: 2 triangular faces (top + bottom) + 3 rectangular side faces = 5
        face_count = result.faces().size()
        assert face_count == 5, \
            f"Face count: expected 5, got {face_count}"
    
        # Edge count: 3 bottom edges + 3 top edges + 3 vertical edges = 9
        edge_count = result.edges().size()
        assert edge_count == 9, \
            f"Edge count: expected 9, got {edge_count}"
    
        # Vertex count: 3 bottom + 3 top = 6
        vertex_count = result.vertices().size()
        assert vertex_count == 6, \
            f"Vertex count: expected 6, got {vertex_count}"
    
        # Planar faces: all 5 faces should be planar (triangular prism)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 5, \
            f"Planar face count: expected 5, got {planar_face_count}"
    
        # Check centroid is near (0, 0, extrude_height/2)
        centroid = cq.Shape.centerOfMass(solid)
        assert abs(centroid.x) < TOL, \
            f"Centroid X: expected ~0, got {centroid.x:.4f}"
        assert abs(centroid.y) < TOL, \
            f"Centroid Y: expected ~0, got {centroid.y:.4f}"
        assert abs(centroid.z - extrude_height / 2) < TOL, \
            f"Centroid Z: expected {extrude_height/2:.4f}, got {centroid.z:.4f}"
    
        # Check a point inside the solid is truly inside
        assert solid.isInside((0, 0, extrude_height / 2)), \
            "Centroid point should be inside the solid"
    
        # Check a point outside the solid is not inside
        assert not solid.isInside((side, side, extrude_height / 2)), \
            "Far corner point should be outside the solid"
    
        print("All assertions passed!")
        print(f"  Side length:    {side} mm")
        print(f"  Extrude height: {extrude_height} mm")
        print(f"  Triangle area:  {triangle_area:.4f} mm²")
        print(f"  Volume:         {solid.Volume():.4f} mm³")
        print(f"  Bounding box:   {bb.xlen:.4f} x {bb.ylen:.4f} x {bb.zlen:.4f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00001977/gpt_generated.stl')
