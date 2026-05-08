import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        half_diag_x = 30.0   # half of horizontal diagonal = 60mm total
        half_diag_y = 20.0   # half of vertical diagonal   = 40mm total
        extrude_h   = 20.0   # extrusion height
    
        # --- Step 1: Build the rhombus profile on the XY plane ---
        # Vertices: right, top, left, bottom
        # (30, 0) -> (0, 20) -> (-30, 0) -> (0, -20) -> close
        result = (
            cq.Workplane("XY")
            .moveTo(half_diag_x, 0)
            .lineTo(0, half_diag_y)
            .lineTo(-half_diag_x, 0)
            .lineTo(0, -half_diag_y)
            .close()
            .extrude(extrude_h)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 2 * half_diag_x) < TOL, \
            f"X length: expected {2*half_diag_x}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * half_diag_y) < TOL, \
            f"Y length: expected {2*half_diag_y}, got {bb.ylen}"
        assert abs(bb.zlen - extrude_h) < TOL, \
            f"Z length (height): expected {extrude_h}, got {bb.zlen}"
    
        # 2. Volume check
        # Volume of extruded rhombus = (d1 * d2 / 2) * height
        # d1 = 60, d2 = 40 => area = 60*40/2 = 1200 mm²
        # volume = 1200 * 20 = 24000 mm³
        diag1 = 2 * half_diag_x   # 60
        diag2 = 2 * half_diag_y   # 40
        expected_area   = (diag1 * diag2) / 2.0   # 1200
        expected_volume = expected_area * extrude_h  # 24000
        actual_volume   = result.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.001, \
            f"Volume: expected {expected_volume:.1f}, got {actual_volume:.1f}"
    
        # 3. Face count
        # An extruded rhombus has:
        #   - 1 bottom face (rhombus)
        #   - 1 top face    (rhombus)
        #   - 4 side faces  (one per edge of the rhombus)
        # Total = 6 faces
        face_count = result.faces().size()
        assert face_count == 6, \
            f"Face count: expected 6, got {face_count}"
    
        # 4. All faces should be planar (no curved surfaces)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, \
            f"Planar face count: expected 6, got {planar_count}"
    
        # 5. Edge count
        # Bottom rhombus: 4 edges
        # Top rhombus:    4 edges
        # Vertical edges: 4 edges (one per vertex of rhombus)
        # Total = 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, \
            f"Edge count: expected 12, got {edge_count}"
    
        # 6. Vertex count
        # 4 bottom vertices + 4 top vertices = 8
        vertex_count = result.vertices().size()
        assert vertex_count == 8, \
            f"Vertex count: expected 8, got {vertex_count}"
    
        # 7. Center of mass should be at (0, 0, extrude_h/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, \
            f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, \
            f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z - extrude_h / 2) < TOL, \
            f"Center of mass Z: expected {extrude_h/2}, got {com.z}"
    
        # 8. Confirm the solid is a single solid
        solid_count = result.solids().size()
        assert solid_count == 1, \
            f"Solid count: expected 1, got {solid_count}"
    
        # 9. Check that the rhombus tip points are on the boundary
        # Right tip at (30, 0, 0) should be on the surface (isInside returns False for surface points,
        # but a point just inside like (29, 0, 10) should be inside)
        inside_pt = result.val().isInside((29.0, 0.0, 10.0))
        assert inside_pt, \
            f"Point (29, 0, 10) should be inside the solid"
    
        outside_pt = result.val().isInside((31.0, 0.0, 10.0))
        assert not outside_pt, \
            f"Point (31, 0, 10) should be outside the solid"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm")
        print(f"  Volume: {actual_volume:.1f} mm³  (expected {expected_volume:.1f})")
        print(f"  Faces: {face_count}, Edges: {edge_count}, Vertices: {vertex_count}")
        print(f"  Center of mass: ({com.x:.3f}, {com.y:.3f}, {com.z:.3f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00038438/gpt_generated.stl')
