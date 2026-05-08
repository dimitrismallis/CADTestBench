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
        outer_width  = 20.0   # outer X dimension
        outer_height = 20.0   # outer Y dimension
        length       = 150.0  # pipe length along Z
        wall_thickness = 2.0  # wall thickness on all sides
    
        inner_width  = outer_width  - 2 * wall_thickness   # 16.0
        inner_height = outer_height - 2 * wall_thickness   # 16.0
    
        # --- Step 1: Create the outer rectangular solid ---
        pipe = cq.Workplane("XY").box(outer_width, outer_height, length)
    
        # --- Step 2: Cut the inner rectangular channel through the length ---
        pipe = (
            pipe
            .faces(">Z")
            .workplane()
            .rect(inner_width, inner_height)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = pipe.val().BoundingBox()
        assert abs(bb.xlen - outer_width)  < TOL, f"X length: expected {outer_width}, got {bb.xlen}"
        assert abs(bb.ylen - outer_height) < TOL, f"Y length: expected {outer_height}, got {bb.ylen}"
        assert abs(bb.zlen - length)       < TOL, f"Z length: expected {length}, got {bb.zlen}"
    
        # Volume check: outer box minus inner channel
        outer_vol = outer_width * outer_height * length
        inner_vol = inner_width * inner_height * length
        expected_vol = outer_vol - inner_vol
        actual_vol = pipe.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count check:
        # A rectangular pipe has:
        # - 4 outer side faces (parallel to Z)
        # - 4 inner side faces (parallel to Z, forming the channel)
        # - 2 top faces (annular top: 1 face with hole = 1 planar face with inner wire)
        # - 2 bottom faces (annular bottom)
        # Actually CadQuery represents the top/bottom as single planar faces with holes
        # Total faces: 4 outer sides + 4 inner sides + 2 end faces = 10
        face_count = pipe.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # Check planar faces: 4 outer sides + 4 inner sides + 2 ends = 10 planar faces
        planar_count = pipe.faces("%Plane").size()
        assert planar_count == 10, f"Planar face count: expected 10, got {planar_count}"
    
        # Check that the pipe is hollow: a point at the center of the cross-section
        # but inside the channel should NOT be inside the solid
        center_of_channel = cq.Vector(0, 0, 0)
        assert not pipe.val().isInside(center_of_channel), \
            "Center of channel should be outside (hollow) the pipe solid"
    
        # Check that a point in the wall IS inside the solid
        point_in_wall = cq.Vector(outer_width / 2 - wall_thickness / 2, 0, 0)
        assert pipe.val().isInside(point_in_wall), \
            f"Point in wall {point_in_wall} should be inside the pipe solid"
    
        # Check symmetry: center of mass should be at origin (0, 0, 0)
        com = cq.Shape.centerOfMass(pipe.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"Center of mass Z: expected 0, got {com.z}"
    
        # Check that the pipe has exactly 1 solid
        solid_count = pipe.solids().size()
        assert solid_count == 1, f"Solid count: expected 1, got {solid_count}"
    
        return pipe
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00670259/gpt_generated.stl')
