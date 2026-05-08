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
        base_length = 0.75
        base_height = 0.284211
        top_length  = 0.347368
        top_height  = 0.135789
        depth       = 0.658737   # extrusion depth (Y direction)
    
        total_height = base_height + top_height  # 0.42
    
        # Half-widths for centering
        base_half = base_length / 2.0   # 0.375
        top_half  = top_length  / 2.0   # 0.173684
    
        # --- Step 1: Build the 2D stepped profile in the XZ plane ---
        # Profile is a closed polygon representing the side view of the pedestal.
        # Points go counter-clockwise starting from bottom-left:
        #
        #   (-top_half, total_height) ---- (top_half, total_height)
        #           |                              |
        #   (-top_half, base_height)   (top_half, base_height)
        #           |                              |
        # (-base_half, base_height) -- (base_half, base_height)
        #           |                              |
        #   (-base_half, 0) ----------- (base_half, 0)
        #
        # In XZ plane: x -> X, y -> Z (workplane XY maps to world XZ)
    
        profile = (
            cq.Workplane("XZ")
            .moveTo(-base_half, 0)
            .lineTo( base_half, 0)
            .lineTo( base_half, base_height)
            .lineTo( top_half,  base_height)
            .lineTo( top_half,  total_height)
            .lineTo(-top_half,  total_height)
            .lineTo(-top_half,  base_height)
            .lineTo(-base_half, base_height)
            .close()
        )
    
        # --- Step 2: Extrude the profile along Y by depth ---
        result = profile.extrude(depth)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - base_length) < TOL, \
            f"X length: expected {base_length}, got {bb.xlen}"
        assert abs(bb.ylen - depth) < TOL, \
            f"Y depth: expected {depth}, got {bb.ylen}"
        assert abs(bb.zlen - total_height) < TOL, \
            f"Z height: expected {total_height}, got {bb.zlen}"
    
        # Volume check:
        # Base block volume + top block volume
        vol_base = base_length * depth * base_height
        vol_top  = top_length  * depth * top_height
        expected_vol = vol_base + vol_top
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: a two-step pedestal extruded from an 8-vertex polygon
        # should have: 2 end faces (front/back) + 8 side faces = 10 planar faces
        face_count = result.faces().size()
        assert face_count == 10, \
            f"Face count: expected 10, got {face_count}"
    
        # All faces should be planar
        planar_count = result.faces("%Plane").size()
        assert planar_count == 10, \
            f"Planar face count: expected 10, got {planar_count}"
    
        # Check top face is at correct Z
        top_z = bb.zmax
        assert abs(top_z - total_height) < TOL, \
            f"Top Z: expected {total_height}, got {top_z}"
    
        # Check bottom face is at Z=0
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Bottom Z: expected 0.0, got {bb.zmin}"
    
        # Check symmetry: center of mass should be at X=0
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, \
            f"Center of mass X: expected 0.0, got {com.x}"
    
        # Check the step: a point inside the top step should be inside the solid
        top_step_point = (0.0, 0.0, base_height + top_height / 2.0)
        assert result.val().isInside(top_step_point), \
            f"Point {top_step_point} should be inside the top step"
    
        # Check a point outside the top step (but above base) is NOT inside
        outside_point = (base_half - 0.01, 0.0, base_height + top_height / 2.0)
        assert not result.val().isInside(outside_point), \
            f"Point {outside_point} should be outside the top step"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00671873/gpt_generated.stl')
