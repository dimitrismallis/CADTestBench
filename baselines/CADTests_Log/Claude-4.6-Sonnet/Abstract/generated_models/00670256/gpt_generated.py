import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        outer_x = 40.0   # outer width
        outer_y = 30.0   # outer depth
        outer_z = 60.0   # height / length of pipe
        wall    = 5.0    # wall thickness
    
        inner_x = outer_x - 2 * wall   # 30.0
        inner_y = outer_y - 2 * wall   # 20.0
    
        # --- Step 1: Create outer rectangular solid ---
        result = cq.Workplane("XY").box(outer_x, outer_y, outer_z)
    
        # --- Step 2: Cut inner rectangular channel through the full height ---
        result = (
            result
            .faces(">Z").workplane()
            .rect(inner_x, inner_y)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box check
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - outer_x) < TOL, f"X length: expected {outer_x}, got {bb.xlen}"
        assert abs(bb.ylen - outer_y) < TOL, f"Y length: expected {outer_y}, got {bb.ylen}"
        assert abs(bb.zlen - outer_z) < TOL, f"Z length: expected {outer_z}, got {bb.zlen}"
    
        # 2. Volume check: outer box minus inner channel
        outer_vol = outer_x * outer_y * outer_z
        inner_vol = inner_x * inner_y * outer_z
        expected_vol = outer_vol - inner_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Face count check:
        # A rectangular pipe has:
        #   - 2 flat end faces (top and bottom annular rings)
        #   - 4 outer side faces (planar)
        #   - 4 inner side faces (planar)
        # Total = 10 planar faces
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # 4. All faces should be planar (no cylindrical faces)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 10, f"Planar face count: expected 10, got {planar_count}"
    
        # 5. Check the hollow is present: a point inside the inner channel
        #    should NOT be inside the solid
        inner_point = (0.0, 0.0, 0.0)  # center of the pipe, inside the hollow
        solid_shape = result.val()
        assert not solid_shape.isInside(inner_point), \
            "Center point should be inside the hollow, not the solid material"
    
        # 6. Check a point in the wall IS inside the solid
        wall_point = (outer_x / 2 - wall / 2, 0.0, 0.0)  # midpoint of right wall
        assert solid_shape.isInside(wall_point), \
            f"Wall point {wall_point} should be inside the solid material"
    
        # 7. Check top and bottom faces exist at correct Z positions
        top_face_z = result.faces(">Z").val().Center().z
        bot_face_z = result.faces("<Z").val().Center().z
        assert abs(top_face_z - outer_z / 2) < TOL, \
            f"Top face Z center: expected {outer_z/2}, got {top_face_z}"
        assert abs(bot_face_z - (-outer_z / 2)) < TOL, \
            f"Bottom face Z center: expected {-outer_z/2}, got {bot_face_z}"
    
        # 8. Symmetry: center of mass should be at origin
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"CoM Z: expected 0, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00670256/gpt_generated.stl')
