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
        outer_size = 0.23077
        inner_size = 0.18462   # outer - 2 * 0.023077 = 0.23077 - 0.04615 = 0.18462
        pipe_length = 0.75
        padding = 0.023077
    
        # --- Step 1: Create outer rectangular pipe body ---
        # Work in XZ plane, extrude along Y-axis
        outer = (
            cq.Workplane("XZ")
            .rect(outer_size, outer_size)
            .extrude(pipe_length)
        )
    
        # --- Step 2: Cut inner hollow ---
        # The inner square is centered at the same point, cut through the full length
        result = (
            outer
            .faces(">Y")
            .workplane()
            .rect(inner_size, inner_size)
            .cutBlind(-pipe_length)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - outer_size) < TOL, \
            f"X length: expected {outer_size}, got {bb.xlen}"
        assert abs(bb.ylen - pipe_length) < TOL, \
            f"Y length (pipe length): expected {pipe_length}, got {bb.ylen}"
        assert abs(bb.zlen - outer_size) < TOL, \
            f"Z length: expected {outer_size}, got {bb.zlen}"
    
        # Volume check: outer box minus inner box
        outer_vol = outer_size * outer_size * pipe_length
        inner_vol = inner_size * inner_size * pipe_length
        expected_vol = outer_vol - inner_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Wall thickness check (should be ~0.023077 on each side)
        wall_thickness = (outer_size - inner_size) / 2
        assert abs(wall_thickness - padding) < TOL, \
            f"Wall thickness: expected {padding}, got {wall_thickness}"
    
        # Face count: a rectangular pipe (hollow square tube) should have 10 planar faces
        # 4 outer side faces + 4 inner side faces + 2 annular end faces = 10 planar faces
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 10, \
            f"Planar face count: expected 10, got {planar_face_count}"
    
        # Check that the center of the bore is hollow (outside the solid)
        center_bore = (0.0, pipe_length / 2, 0.0)
        is_hollow = not result.val().isInside(center_bore, tolerance=1e-4)
        assert is_hollow, \
            f"Center of bore {center_bore} should be hollow, but isInside returned True"
    
        # Check symmetry: center of mass should be at (0, pipe_length/2, 0)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, \
            f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y - pipe_length / 2) < TOL, \
            f"Center of mass Y: expected {pipe_length/2}, got {com.y}"
        assert abs(com.z) < TOL, \
            f"Center of mass Z: expected 0, got {com.z}"
    
        # Verify the pipe has exactly 1 solid
        solid_count = result.solids().size()
        assert solid_count == 1, \
            f"Expected 1 solid, got {solid_count}"
    
        # Verify total face count (10 planar faces for a hollow square tube)
        total_face_count = result.faces().size()
        assert total_face_count == 10, \
            f"Total face count: expected 10, got {total_face_count}"
    
        # Verify there are exactly 2 end faces (perpendicular to Y-axis / pipe axis)
        end_faces = result.faces("|Y").size()
        assert end_faces == 2, \
            f"End faces (perpendicular to pipe axis): expected 2, got {end_faces}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00037494/gpt_generated.stl')
