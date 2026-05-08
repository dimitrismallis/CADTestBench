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
        # L-shape profile dimensions
        total_height = 80.0    # total height of the vertical leg
        total_width  = 60.0    # total width of the horizontal leg
        thickness    = 15.0    # thickness of both legs
        extrude_len  = 100.0   # extrusion length (makes it "long")
    
        # --- Step 1: Draw the L-shaped sketch on the XY plane ---
        # The L is drawn as a closed polygon with 6 vertices:
        #   Starting at bottom-left corner, going clockwise:
        #   (0,0) -> (total_width, 0) -> (total_width, thickness) ->
        #   (thickness, thickness) -> (thickness, total_height) ->
        #   (0, total_height) -> back to (0,0)
        #
        # This creates:
        #   - Horizontal leg: full width (60mm) × thickness (15mm) at the bottom
        #   - Vertical leg: thickness (15mm) × full height (80mm) on the left
    
        result = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(total_width, 0)
            .lineTo(total_width, thickness)
            .lineTo(thickness, thickness)
            .lineTo(thickness, total_height)
            .lineTo(0, total_height)
            .close()
            .extrude(extrude_len)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - total_width)  < TOL, f"X extent: expected {total_width}, got {bb.xlen}"
        assert abs(bb.ylen - total_height) < TOL, f"Y extent: expected {total_height}, got {bb.ylen}"
        assert abs(bb.zlen - extrude_len)  < TOL, f"Z extent (extrusion): expected {extrude_len}, got {bb.zlen}"
    
        # 2. Volume check
        # L cross-section area = total_width * thickness + (total_height - thickness) * thickness
        #                      = 60*15 + (80-15)*15 = 900 + 975 = 1875 mm²
        cross_section_area = total_width * thickness + (total_height - thickness) * thickness
        expected_volume = cross_section_area * extrude_len
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.001, \
            f"Volume: expected {expected_volume:.1f}, got {actual_volume:.1f}"
    
        # 3. Face count check
        # An extruded L-shape (6-sided polygon) should have:
        #   - 2 end faces (front and back, each L-shaped)
        #   - 6 side faces (one per edge of the L polygon)
        # Total = 8 faces
        face_count = result.faces().size()
        assert face_count == 8, f"Face count: expected 8, got {face_count}"
    
        # 4. All faces should be planar (no curved surfaces)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 8, f"Planar faces: expected 8, got {planar_face_count}"
    
        # 5. Check top face (max Z) is at extrude_len
        assert abs(bb.zmax - extrude_len) < TOL, f"Max Z: expected {extrude_len}, got {bb.zmax}"
        assert abs(bb.zmin - 0.0) < TOL, f"Min Z: expected 0.0, got {bb.zmin}"
    
        # 6. Check the L-shape bounding extents
        assert abs(bb.xmin - 0.0) < TOL, f"Min X: expected 0.0, got {bb.xmin}"
        assert abs(bb.xmax - total_width) < TOL, f"Max X: expected {total_width}, got {bb.xmax}"
        assert abs(bb.ymin - 0.0) < TOL, f"Min Y: expected 0.0, got {bb.ymin}"
        assert abs(bb.ymax - total_height) < TOL, f"Max Y: expected {total_height}, got {bb.ymax}"
    
        # 7. Verify the inner corner point is NOT inside the solid
        # The inner corner of the L is at (thickness, thickness, extrude_len/2)
        # A point just inside the "missing" quadrant should be outside the solid
        inner_void_point = cq.Vector(thickness + 5, thickness + 5, extrude_len / 2)
        assert not result.val().isInside(inner_void_point), \
            f"Point {inner_void_point} should be outside the L-shape (in the void region)"
    
        # 8. Verify a point clearly inside the vertical leg is inside the solid
        inside_vertical = cq.Vector(thickness / 2, total_height / 2, extrude_len / 2)
        assert result.val().isInside(inside_vertical), \
            f"Point {inside_vertical} should be inside the vertical leg"
    
        # 9. Verify a point clearly inside the horizontal leg is inside the solid
        inside_horizontal = cq.Vector(total_width / 2, thickness / 2, extrude_len / 2)
        assert result.val().isInside(inside_horizontal), \
            f"Point {inside_horizontal} should be inside the horizontal leg"
    
        # 10. Edge count: extruded 6-sided polygon → 6*3 = 18 edges
        edge_count = result.edges().size()
        assert edge_count == 18, f"Edge count: expected 18, got {edge_count}"
    
        # 11. Vertex count: 6 vertices per end face × 2 = 12 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 12, f"Vertex count: expected 12, got {vertex_count}"
    
        print(f"✓ Bounding box: {bb.xlen:.1f} × {bb.ylen:.1f} × {bb.zlen:.1f} mm")
        print(f"✓ Volume: {actual_volume:.1f} mm³ (expected {expected_volume:.1f} mm³)")
        print(f"✓ Faces: {face_count}, Edges: {edge_count}, Vertices: {vertex_count}")
        print(f"✓ Cross-section area: {cross_section_area:.1f} mm²")
        print("✓ All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00672291/gpt_generated.stl')
