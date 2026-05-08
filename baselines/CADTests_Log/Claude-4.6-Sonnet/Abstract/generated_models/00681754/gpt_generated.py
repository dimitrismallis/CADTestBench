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
        rect_length = 80.0   # X dimension of base block
        rect_width  = 40.0   # Y dimension of base block
        rect_height = 20.0   # Z dimension (height) of base block
    
        cyl_diameter = rect_length / 4.0   # = 20 mm  (~1/4 of length)
        cyl_radius   = cyl_diameter / 2.0  # = 10 mm
        cyl_height   = 30.0                # height of cylinder on top
    
        # --- Step 1: Draw rectangle sketch and extrude to form base block ---
        base = (
            cq.Workplane("XY")
            .rect(rect_length, rect_width)
            .extrude(rect_height)
        )
    
        # --- Step 2: Select top face, draw circle at center, extrude upward ---
        result = (
            base
            .faces(">Z")
            .workplane()
            .circle(cyl_radius)
            .extrude(cyl_height)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Overall bounding box
        bb = result.val().BoundingBox()
        total_height = rect_height + cyl_height  # 20 + 30 = 50
        assert abs(bb.xlen - rect_length) < TOL, \
            f"BBox X: expected {rect_length}, got {bb.xlen}"
        assert abs(bb.ylen - rect_width) < TOL, \
            f"BBox Y: expected {rect_width}, got {bb.ylen}"
        assert abs(bb.zlen - total_height) < TOL, \
            f"BBox Z: expected {total_height}, got {bb.zlen}"
    
        # 2. Volume check
        block_vol = rect_length * rect_width * rect_height
        cyl_vol   = math.pi * cyl_radius**2 * cyl_height
        expected_vol = block_vol + cyl_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Cylindrical face count — the cylinder contributes 1 curved face
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, \
            f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # 4. Planar face count
        # Base block: 6 faces, but top face is partially covered by cylinder
        # Cylinder adds: 1 top circle + 1 bottom circle (coincident with block top, merged)
        # After union: bottom(1) + 4 sides of block(4) + annular ring on top(1) +
        #              cylinder curved(1) + cylinder top(1) = 8 planar + 1 cylindrical
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 7, \
            f"Planar faces: expected at least 7, got {planar_faces}"
    
        # 5. The top of the cylinder should be at z = total_height
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - total_height) < TOL, \
            f"Top face Z center: expected {total_height}, got {top_face_z}"
    
        # 6. Bottom face should be at z = 0
        bot_face_z = result.faces("<Z").val().Center().z
        assert abs(bot_face_z - 0.0) < TOL, \
            f"Bottom face Z center: expected 0.0, got {bot_face_z}"
    
        # 7. Center of mass should be near x=0, y=0 (symmetric)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected ~0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected ~0, got {com.y}"
    
        # 8. Cylinder top circular edge check
        circ_edges = result.edges("%Circle").size()
        assert circ_edges >= 2, \
            f"Circular edges: expected at least 2 (top + bottom of cylinder), got {circ_edges}"
    
        # 9. Point inside the cylinder portion should be inside the solid
        cyl_interior_pt = (0, 0, rect_height + cyl_height / 2.0)
        assert result.val().isInside(cyl_interior_pt), \
            f"Point {cyl_interior_pt} should be inside the cylinder portion"
    
        # 10. Point inside the base block should be inside the solid
        block_interior_pt = (rect_length / 4.0, rect_width / 4.0, rect_height / 2.0)
        assert result.val().isInside(block_interior_pt), \
            f"Point {block_interior_pt} should be inside the base block"
    
        # 11. Point outside the solid (above cylinder, off-center) should NOT be inside
        outside_pt = (rect_length / 2.0, rect_width / 2.0, rect_height + cyl_height / 2.0)
        assert not result.val().isInside(outside_pt), \
            f"Point {outside_pt} should be outside the solid"
    
        print("All assertions passed!")
        print(f"  Base block: {rect_length} x {rect_width} x {rect_height} mm")
        print(f"  Cylinder:   diameter={cyl_diameter} mm, height={cyl_height} mm")
        print(f"  Total height: {total_height} mm")
        print(f"  Volume: {actual_vol:.2f} mm³ (expected {expected_vol:.2f} mm³)")
        print(f"  Cylindrical faces: {cyl_faces}")
        print(f"  Planar faces: {planar_faces}")
        print(f"  Circular edges: {circ_edges}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00681754/gpt_generated.stl')
