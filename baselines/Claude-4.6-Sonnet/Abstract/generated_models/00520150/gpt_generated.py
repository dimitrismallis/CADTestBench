import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        total_width  = 40.0   # total width of L (horizontal extent)
        total_height = 60.0   # total height of L (vertical extent)
        bar_thickness = 20.0  # thickness of both bars
        extrude_depth = 10.0  # extrusion depth along Z
    
        # --- Step 1: Define the L-shape profile as a closed 2D wire ---
        # The L is drawn starting from the bottom-left corner, going clockwise:
        #
        #  (0,60) ─────── (20,60)
        #    |                |
        #    |                |
        #    |                |
        #  (0,20) ─── (40,20)─(40,0)
        #    |                      |
        #  (0,0) ──────────────── (40,0)  <- bottom
        #
        # Vertices (counter-clockwise for correct normal):
        # (0,0) → (40,0) → (40,20) → (20,20) → (20,60) → (0,60) → close
    
        result = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(total_width, 0)                  # bottom edge
            .lineTo(total_width, bar_thickness)       # right side of horizontal bar
            .lineTo(bar_thickness, bar_thickness)     # inner corner
            .lineTo(bar_thickness, total_height)      # right side of vertical bar
            .lineTo(0, total_height)                  # top edge
            .close()                                  # back to (0,0)
            .extrude(extrude_depth)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box check
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - total_width)   < TOL, f"X length: expected {total_width}, got {bb.xlen}"
        assert abs(bb.ylen - total_height)  < TOL, f"Y length: expected {total_height}, got {bb.ylen}"
        assert abs(bb.zlen - extrude_depth) < TOL, f"Z length: expected {extrude_depth}, got {bb.zlen}"
    
        # 2. Volume check
        # L-shape area = total_width * bar_thickness + bar_thickness * (total_height - bar_thickness)
        l_area = total_width * bar_thickness + bar_thickness * (total_height - bar_thickness)
        expected_volume = l_area * extrude_depth
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.001, \
            f"Volume: expected {expected_volume:.2f}, got {actual_volume:.2f}"
    
        # 3. Face count check
        # An extruded L-shape (6-sided polygon) should have:
        # - 2 flat faces (top and bottom)
        # - 6 side faces (one per edge of the L profile)
        # Total = 8 faces
        face_count = result.faces().size()
        assert face_count == 8, f"Face count: expected 8, got {face_count}"
    
        # 4. Edge count check
        # Each flat face has 6 edges, 6 side faces have 4 edges each
        # But shared edges are counted once: 6 (top) + 6 (bottom) + 6 (vertical sides) = 18 edges
        edge_count = result.edges().size()
        assert edge_count == 18, f"Edge count: expected 18, got {edge_count}"
    
        # 5. Vertex count check
        # 6 vertices on top + 6 on bottom = 12 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 12, f"Vertex count: expected 12, got {vertex_count}"
    
        # 6. Check top and bottom planar faces exist
        top_faces    = result.faces(">Z").size()
        bottom_faces = result.faces("<Z").size()
        assert top_faces    == 1, f"Top face count: expected 1, got {top_faces}"
        assert bottom_faces == 1, f"Bottom face count: expected 1, got {bottom_faces}"
    
        # 7. Check that the inner corner point is NOT inside the solid
        # The missing square region (top-right) should be outside the solid
        inner_point = (30.0, 40.0, 5.0)  # inside the missing square of the L
        assert not result.val().isInside(inner_point), \
            f"Point {inner_point} should be outside the L-shape solid"
    
        # 8. Check that a point inside the vertical bar IS inside the solid
        vert_bar_point = (10.0, 40.0, 5.0)  # inside the vertical bar
        assert result.val().isInside(vert_bar_point), \
            f"Point {vert_bar_point} should be inside the L-shape solid"
    
        # 9. Check that a point inside the horizontal bar IS inside the solid
        horiz_bar_point = (30.0, 10.0, 5.0)  # inside the horizontal bar
        assert result.val().isInside(horiz_bar_point), \
            f"Point {horiz_bar_point} should be inside the L-shape solid"
    
        # 10. Center of mass check (should be offset toward the L's corner)
        com = cq.Shape.centerOfMass(result.val())
        # CoM X should be less than total_width/2 (biased toward left bar)
        assert com.x < total_width / 2, \
            f"CoM X ({com.x:.2f}) should be < {total_width/2} (biased toward vertical bar)"
        # CoM Y should be less than total_height/2 (biased toward bottom bar)
        assert com.y < total_height / 2, \
            f"CoM Y ({com.y:.2f}) should be < {total_height/2} (biased toward horizontal bar)"
        # CoM Z should be at half the extrusion depth
        assert abs(com.z - extrude_depth / 2) < TOL, \
            f"CoM Z: expected {extrude_depth/2}, got {com.z:.4f}"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen} x {bb.ylen} x {bb.zlen} mm")
        print(f"  Volume: {actual_volume:.2f} mm³ (expected {expected_volume:.2f})")
        print(f"  Faces: {face_count}, Edges: {edge_count}, Vertices: {vertex_count}")
        print(f"  Center of mass: ({com.x:.2f}, {com.y:.2f}, {com.z:.2f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00520150/gpt_generated.stl')
