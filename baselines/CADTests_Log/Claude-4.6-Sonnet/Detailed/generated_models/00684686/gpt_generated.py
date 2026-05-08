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
        plate_x = 0.231564   # length in X
        plate_y = 0.028954   # width in Y
        plate_z = 0.926255   # height in Z
    
        hole_x = 0.12897     # hole length in X
        hole_z = 0.479215    # hole height in Z
        gap_z  = 0.005463    # gap from bottom of plate to bottom of hole
    
        translate = (-0.050509, -0.014477, 0.286873)
    
        # --- Step 1: Create the base plate ---
        # Box centered at origin: X in [-plate_x/2, plate_x/2],
        #                          Y in [-plate_y/2, plate_y/2],
        #                          Z in [-plate_z/2, plate_z/2]
        result = cq.Workplane("XY").box(plate_x, plate_y, plate_z)
    
        # --- Step 2: Create the rectangular hole ---
        # The hole is:
        #   - hole_x wide in X, centered at X=0
        #   - hole_z tall in Z
        #   - positioned so its bottom is at gap_z from the plate bottom
        #   - plate bottom is at Z = -plate_z/2
        #   - hole bottom Z = -plate_z/2 + gap_z
        #   - hole center Z = -plate_z/2 + gap_z + hole_z/2
        #   - cuts through full Y thickness
    
        hole_center_z = -plate_z / 2 + gap_z + hole_z / 2
    
        # Sketch on the XZ plane (front face, Y face) and cut through all in Y
        # Use the front face (max Y face) as workplane, sketch the rectangle, cutThruAll
        result = (
            result
            .faces(">Y")
            .workplane()
            .center(0, hole_center_z)   # center(x_offset, z_offset) in face local coords
            .rect(hole_x, hole_z)
            .cutThruAll()
        )
    
        # --- Step 3: Translate the entire part ---
        result = result.translate(translate)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # After translation, bounding box should be:
        # X: -plate_x/2 + tx to plate_x/2 + tx
        # Y: -plate_y/2 + ty to plate_y/2 + ty
        # Z: -plate_z/2 + tz to plate_z/2 + tz
        tx, ty, tz = translate
        expected_xmin = -plate_x/2 + tx
        expected_xmax =  plate_x/2 + tx
        expected_ymin = -plate_y/2 + ty
        expected_ymax =  plate_y/2 + ty
        expected_zmin = -plate_z/2 + tz
        expected_zmax =  plate_z/2 + tz
    
        assert abs(bb.xlen - plate_x) < TOL, f"X length: expected {plate_x}, got {bb.xlen}"
        assert abs(bb.ylen - plate_y) < TOL, f"Y length: expected {plate_y}, got {bb.ylen}"
        assert abs(bb.zlen - plate_z) < TOL, f"Z length: expected {plate_z}, got {bb.zlen}"
    
        assert abs(bb.xmin - expected_xmin) < TOL, f"xmin: expected {expected_xmin}, got {bb.xmin}"
        assert abs(bb.xmax - expected_xmax) < TOL, f"xmax: expected {expected_xmax}, got {bb.xmax}"
        assert abs(bb.ymin - expected_ymin) < TOL, f"ymin: expected {expected_ymin}, got {bb.ymin}"
        assert abs(bb.ymax - expected_ymax) < TOL, f"ymax: expected {expected_ymax}, got {bb.ymax}"
        assert abs(bb.zmin - expected_zmin) < TOL, f"zmin: expected {expected_zmin}, got {bb.zmin}"
        assert abs(bb.zmax - expected_zmax) < TOL, f"zmax: expected {expected_zmax}, got {bb.zmax}"
    
        # Volume check:
        # Plate volume minus hole volume
        plate_vol = plate_x * plate_y * plate_z
        hole_vol  = hole_x * plate_y * hole_z   # hole cuts through full Y
        expected_vol = plate_vol - hole_vol
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that the hole exists: a point inside the hole region should be outside the solid
        # Hole center in world coords (after translation):
        hole_world_x = 0 + tx
        hole_world_y = 0 + ty   # center of Y
        hole_world_z = hole_center_z + tz
        hole_test_point = (hole_world_x, hole_world_y, hole_world_z)
        assert not solid.isInside(hole_test_point, tolerance=1e-5), \
            f"Point {hole_test_point} should be inside the hole (outside solid), but it's inside"
    
        # Check that a point in the solid (above the hole) is inside
        solid_test_z = -plate_z/2 + gap_z + hole_z + 0.05 + tz  # above the hole
        solid_test_point = (0 + tx, 0 + ty, solid_test_z)
        assert solid.isInside(solid_test_point, tolerance=1e-5), \
            f"Point {solid_test_point} should be inside the solid, but it's not"
    
        # Check face count: base box has 6 faces, hole adds 4 more faces (top, bottom, left, right of hole)
        # but removes 0 (hole goes through Y, so front and back faces get modified)
        # Expected: 6 original + 4 hole interior faces = 10 faces
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: X=[{bb.xmin:.6f}, {bb.xmax:.6f}], Y=[{bb.ymin:.6f}, {bb.ymax:.6f}], Z=[{bb.zmin:.6f}, {bb.zmax:.6f}]")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Face count: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00684686/gpt_generated.stl')
