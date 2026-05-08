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
        # Step widths (half-widths for symmetric profile)
        w1 = 45   # half-width of base step
        w2 = 30   # half-width of step 2
        w3 = 15   # half-width of step 3 (top)
    
        h1 = 20   # height of step 1
        h2 = 20   # height of step 2
        h3 = 20   # height of step 3
    
        depth = 90  # extrusion depth (Y direction)
    
        # --- Step 1: Build the side profile as a closed 2D wire on XZ plane ---
        # Profile points (X, Z) going around the staircase outline:
        # Bottom-left → bottom-right → up step1 right → in to step2 right →
        # up step2 right → in to step3 right → up step3 → across top →
        # down step3 left → out to step2 left → down step2 left →
        # out to step1 left → back to start
    
        profile = (
            cq.Workplane("XZ")
            .moveTo(-w1, 0)
            .lineTo( w1, 0)            # bottom edge
            .lineTo( w1, h1)           # right side of step 1
            .lineTo( w2, h1)           # step 1 top going inward (right)
            .lineTo( w2, h1+h2)        # right side of step 2
            .lineTo( w3, h1+h2)        # step 2 top going inward (right)
            .lineTo( w3, h1+h2+h3)     # right side of step 3
            .lineTo(-w3, h1+h2+h3)     # top of step 3
            .lineTo(-w3, h1+h2)        # left side of step 3
            .lineTo(-w2, h1+h2)        # step 2 top going outward (left)
            .lineTo(-w2, h1)           # left side of step 2
            .lineTo(-w1, h1)           # step 1 top going outward (left)
            .close()                   # back to start (-w1, 0)
        )
    
        # --- Step 2: Extrude the profile in the Y direction ---
        result = profile.extrude(depth)
    
        # --- Determine actual Y extents for assertions ---
        bb = result.val().BoundingBox()
        y_mid = (bb.ymin + bb.ymax) / 2.0
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        total_width  = 2 * w1          # 90
        total_height = h1 + h2 + h3   # 60
        total_depth  = depth           # 90
    
        assert abs(bb.xlen - total_width)  < TOL, f"X width: expected {total_width}, got {bb.xlen}"
        assert abs(bb.ylen - total_depth)  < TOL, f"Y depth: expected {total_depth}, got {bb.ylen}"
        assert abs(bb.zlen - total_height) < TOL, f"Z height: expected {total_height}, got {bb.zlen}"
    
        # Bounding box origin checks (centered in X, starts at Z=0)
        assert abs(bb.xmin - (-w1)) < TOL, f"xmin: expected {-w1}, got {bb.xmin}"
        assert abs(bb.xmax -  w1)   < TOL, f"xmax: expected {w1}, got {bb.xmax}"
        assert abs(bb.zmin - 0)     < TOL, f"zmin: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - total_height) < TOL, f"zmax: expected {total_height}, got {bb.zmax}"
    
        # Volume check: sum of three rectangular prisms
        vol_step1 = (2*w1) * h1 * depth
        vol_step2 = (2*w2) * h2 * depth
        vol_step3 = (2*w3) * h3 * depth
        expected_vol = vol_step1 + vol_step2 + vol_step3
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Face count: the extruded staircase profile should have 14 faces
        # (12 side faces from the 12-segment profile + 2 end faces)
        face_count = result.faces().size()
        assert face_count == 14, f"Face count: expected 14, got {face_count}"
    
        # All faces should be planar (no curves)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 14, f"Planar face count: expected 14, got {planar_count}"
    
        # Check symmetry: center of mass should be at x=0 (symmetric about YZ plane)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
    
        # Check that the top step is at the correct height
        top_face = result.faces(">Z")
        top_bb = top_face.val().BoundingBox()
        assert abs(top_bb.zmin - total_height) < TOL, f"Top face Z: expected {total_height}, got {top_bb.zmin}"
        assert abs(top_bb.xlen - 2*w3) < TOL, f"Top face width: expected {2*w3}, got {top_bb.xlen}"
    
        # Use y_mid (actual center of Y extent) for interior point checks
        # Point well inside the base step: x=35 (< w1=45), z=10 (< h1=20)
        assert result.val().isInside((35, y_mid, 10)), \
            f"Point (35, {y_mid}, 10) inside base step should be inside solid"
    
        # Point outside step 2 width (x=40 > w2=30) at z=30 (in step 2 height range)
        assert not result.val().isInside((40, y_mid, 30)), \
            f"Point (40, {y_mid}, 30) outside step 2 should be outside solid"
    
        # Point inside top step: x=10 (< w3=15), z=50 (in step 3 height range)
        assert result.val().isInside((10, y_mid, 50)), \
            f"Point (10, {y_mid}, 50) inside top step should be inside solid"
    
        # Point outside top step: x=20 (> w3=15), z=50 (in step 3 height range)
        assert not result.val().isInside((20, y_mid, 50)), \
            f"Point (20, {y_mid}, 50) outside top step should be outside solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00682075/gpt_generated.stl')
