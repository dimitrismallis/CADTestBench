import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        large_side = 20.0   # side length of the base square
        small_side = 16.0   # side length of the top square
        extrude_h  = 2.0    # extrusion height for each layer
    
        # --- Step 1: Base square layer ---
        # Create a 20x20 square sketch on XY plane and extrude 2mm upward
        result = (
            cq.Workplane("XY")
            .rect(large_side, large_side)
            .extrude(extrude_h)
        )
    
        # --- Step 2: Top square layer ---
        # On the top face of the base, create a 16x16 square centered at the same
        # XY position and extrude another 2mm upward
        result = (
            result
            .faces(">Z")
            .workplane()
            .rect(small_side, small_side)
            .extrude(extrude_h)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - large_side) < TOL, \
            f"X extent: expected {large_side}, got {bb.xlen}"
        assert abs(bb.ylen - large_side) < TOL, \
            f"Y extent: expected {large_side}, got {bb.ylen}"
        assert abs(bb.zlen - 2 * extrude_h) < TOL, \
            f"Z extent: expected {2 * extrude_h}, got {bb.zlen}"
    
        # Bounding box position (centered in XY, base at Z=0)
        assert abs(bb.xmin - (-large_side / 2)) < TOL, \
            f"xmin: expected {-large_side/2}, got {bb.xmin}"
        assert abs(bb.ymin - (-large_side / 2)) < TOL, \
            f"ymin: expected {-large_side/2}, got {bb.ymin}"
        assert abs(bb.zmin - 0.0) < TOL, \
            f"zmin: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - 2 * extrude_h) < TOL, \
            f"zmax: expected {2 * extrude_h}, got {bb.zmax}"
    
        # Volume check: base layer + top layer
        vol_base = large_side * large_side * extrude_h   # 20*20*2 = 800
        vol_top  = small_side * small_side * extrude_h   # 16*16*2 = 512
        expected_vol = vol_base + vol_top                 # 1312
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) < TOL, \
            f"Volume: expected {expected_vol}, got {actual_vol}"
    
        # Face count check:
        # Bottom face: 1 (large square bottom, Z=0)
        # Top face: 1 (small square top, Z=4)
        # Ledge face: 1 (annular step at Z=2, one planar face with inner boundary)
        # Outer sides of base: 4 (large square sides, Z=0 to Z=2)
        # Sides of top: 4 (small square sides, Z=2 to Z=4)
        # Total planar faces: 1 + 1 + 1 + 4 + 4 = 11
        n_faces = result.faces("%Plane").size()
        assert n_faces == 11, \
            f"Planar face count: expected 11, got {n_faces}"
    
        # Horizontal faces (normals parallel to Z axis): bottom + top + ledge = 3
        # Selector |Z finds faces whose normal is parallel to Z (i.e., horizontal faces)
        horiz_faces = result.faces("|Z").size()
        assert horiz_faces == 3, \
            f"Horizontal face count (|Z): expected 3, got {horiz_faces}"
    
        # Vertical side faces (normals perpendicular to Z): 4 base sides + 4 top sides = 8
        # Selector #Z finds faces whose normal is perpendicular to Z (i.e., vertical faces)
        vert_faces = result.faces("#Z").size()
        assert vert_faces == 8, \
            f"Vertical face count (#Z): expected 8, got {vert_faces}"
    
        # Top face should be at Z = 2*extrude_h
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - 2 * extrude_h) < TOL, \
            f"Top face Z center: expected {2 * extrude_h}, got {top_face_z}"
    
        # Bottom face should be at Z = 0
        bot_face_z = result.faces("<Z").val().Center().z
        assert abs(bot_face_z - 0.0) < TOL, \
            f"Bottom face Z center: expected 0.0, got {bot_face_z}"
    
        # Center of mass should be at (0, 0) in XY (symmetric)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
    
        # The top square is smaller — verify top face area
        top_face_area = result.faces(">Z").val().Area()
        expected_top_area = small_side * small_side   # 16*16 = 256
        assert abs(top_face_area - expected_top_area) < TOL, \
            f"Top face area: expected {expected_top_area}, got {top_face_area}"
    
        # The bottom face area should match the large square
        bot_face_area = result.faces("<Z").val().Area()
        expected_bot_area = large_side * large_side   # 20*20 = 400
        assert abs(bot_face_area - expected_bot_area) < TOL, \
            f"Bottom face area: expected {expected_bot_area}, got {bot_face_area}"
    
        # Verify the ledge face at mid-height Z=2
        # The ledge face area = large_square_area - small_square_area
        # = 20*20 - 16*16 = 400 - 256 = 144
        # The ledge is the only horizontal face at Z=2 (not top, not bottom)
        # We can check by finding the face at Z=extrude_h
        ledge_area_expected = large_side**2 - small_side**2  # 400 - 256 = 144
        # Get all horizontal faces and find the one at Z=extrude_h (the ledge)
        horiz_face_list = result.faces("|Z").vals()
        ledge_faces = [f for f in horiz_face_list
                       if abs(f.Center().z - extrude_h) < TOL]
        assert len(ledge_faces) == 1, \
            f"Ledge face count at Z={extrude_h}: expected 1, got {len(ledge_faces)}"
        assert abs(ledge_faces[0].Area() - ledge_area_expected) < TOL, \
            f"Ledge face area: expected {ledge_area_expected}, got {ledge_faces[0].Area()}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00676218/gpt_generated.stl')
