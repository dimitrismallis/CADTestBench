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
        outer_size = 30.0    # outer square side length (mm)
        inner_size = 24.0    # inner square side length (mm), 3mm wall thickness
        pipe_length = 80.0   # length along Y-axis (mm)
    
        # --- Step 1: Create outer square in X-Z plane and extrude along Y ---
        # The XZ workplane normal points in -Y, so extrude goes along -Y.
        # The pipe will span from Y=0 to Y=-80.
        outer = (
            cq.Workplane("XZ")
            .rect(outer_size, outer_size)   # square in X-Z plane
            .extrude(pipe_length)           # extrude along -Y (XZ plane normal)
        )
    
        # --- Step 2: Create inner square (hole) in X-Z plane, same center,
        #             cut through the solid to hollow it out ---
        result = (
            outer
            .faces("<Y")                    # select the face at minimum Y (far end)
            .workplane()                    # set workplane on that face
            .rect(inner_size, inner_size)   # smaller square, same center
            .cutThruAll()                   # cut through the entire solid
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        # 1. Bounding box checks
        solid_shape = result.val()
        bb = solid_shape.BoundingBox()
    
        assert abs(bb.xlen - outer_size) < TOL, \
            f"X extent: expected {outer_size}, got {bb.xlen}"
        assert abs(bb.ylen - pipe_length) < TOL, \
            f"Y extent (pipe length): expected {pipe_length}, got {bb.ylen}"
        assert abs(bb.zlen - outer_size) < TOL, \
            f"Z extent: expected {outer_size}, got {bb.zlen}"
    
        # 2. Volume check: outer box minus inner channel
        outer_vol = outer_size * outer_size * pipe_length
        inner_vol = inner_size * inner_size * pipe_length
        expected_vol = outer_vol - inner_vol
        actual_vol = solid_shape.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Face count check:
        # A rectangular hollow pipe has:
        # - 2 end faces (rectangular rings at each end)
        # - 4 outer side faces (parallel to Y-axis)
        # - 4 inner side faces (forming the hole walls)
        # Total = 10 planar faces
        face_count = result.faces().size()
        assert face_count == 10, \
            f"Face count: expected 10, got {face_count}"
    
        # 4. All faces should be planar (no cylindrical faces)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 10, \
            f"Planar face count: expected 10, got {planar_count}"
    
        # 5. Compute mid_y from actual bounding box for robust point checks
        mid_y = (bb.ymin + bb.ymax) / 2.0
    
        # 6. Check the pipe is hollow: center of inner channel should be OUTSIDE solid
        inner_point = cq.Vector(0.0, mid_y, 0.0)
        assert not solid_shape.isInside(inner_point), \
            "Center of inner channel should be outside the solid (pipe is hollow)"
    
        # 7. Check a point in the X-direction wall IS inside the solid
        # Wall spans from inner_size/2=12 to outer_size/2=15 in X; midpoint = 13.5
        wall_x = (inner_size / 2.0 + outer_size / 2.0) / 2.0  # = 13.5
        wall_point_x = cq.Vector(wall_x, mid_y, 0.0)
        assert solid_shape.isInside(wall_point_x), \
            f"Point ({wall_x}, {mid_y}, 0) in the pipe wall (X side) should be inside the solid"
    
        # 8. Check a point in the Z-direction wall IS inside the solid
        wall_z = (inner_size / 2.0 + outer_size / 2.0) / 2.0  # = 13.5
        wall_point_z = cq.Vector(0.0, mid_y, wall_z)
        assert solid_shape.isInside(wall_point_z), \
            f"Point (0, {mid_y}, {wall_z}) in the pipe wall (Z side) should be inside the solid"
    
        # 9. Check symmetry: center of mass
        # XZ plane normal is -Y, so pipe spans Y=0 to Y=-pipe_length
        # Center of mass should be at (0, -pipe_length/2, 0)
        com = cq.Shape.centerOfMass(solid_shape)
        expected_com_y = -(pipe_length / 2.0)
        assert abs(com.x) < TOL, \
            f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y - expected_com_y) < TOL, \
            f"Center of mass Y: expected {expected_com_y}, got {com.y}"
        assert abs(com.z) < TOL, \
            f"Center of mass Z: expected 0, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00037494/gpt_generated.stl')
