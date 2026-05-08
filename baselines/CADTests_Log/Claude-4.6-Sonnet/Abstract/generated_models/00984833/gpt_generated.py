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
        length = 80.0       # shared length (X)
        width_base = 60.0   # base rectangle width (Y)
        width_top = 40.0    # top rectangle width (Y) — slightly smaller
        extrude_h = 20.0    # extrusion height for each tier
    
        # --- Step 1: Create base rectangle and extrude ---
        base = cq.Workplane("XY").rect(length, width_base).extrude(extrude_h)
    
        # --- Step 2: Create top tier — same length, smaller width, centered, same extrusion height ---
        result = (
            base
            .faces(">Z")
            .workplane()
            .rect(length, width_top)
            .extrude(extrude_h)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Overall bounding box
        bb = result.val().BoundingBox()
    
        # X extent: same length for both tiers → 80
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
    
        # Y extent: base is wider (60) → overall Y = 60
        assert abs(bb.ylen - width_base) < TOL, f"Y width: expected {width_base}, got {bb.ylen}"
    
        # Z extent: two tiers stacked → 2 * extrude_h = 40
        total_height = 2 * extrude_h
        assert abs(bb.zlen - total_height) < TOL, f"Z height: expected {total_height}, got {bb.zlen}"
    
        # Bounding box Z starts at 0
        assert abs(bb.zmin) < TOL, f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - total_height) < TOL, f"Z max: expected {total_height}, got {bb.zmax}"
    
        # Volume: base box + top box
        vol_base = length * width_base * extrude_h
        vol_top  = length * width_top  * extrude_h
        expected_vol = vol_base + vol_top
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Center of mass should be at X=0, Y=0 (symmetric in XY)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
    
        # Top face (>Z) should have the top tier dimensions
        top_face = result.faces(">Z").val()
        top_bb = top_face.BoundingBox()
        assert abs(top_bb.xlen - length) < TOL, f"Top face X: expected {length}, got {top_bb.xlen}"
        assert abs(top_bb.ylen - width_top) < TOL, f"Top face Y: expected {width_top}, got {top_bb.ylen}"
    
        # Bottom face (<Z) should have the full base width
        bot_face = result.faces("<Z").val()
        bot_bb = bot_face.BoundingBox()
        assert abs(bot_bb.xlen - length) < TOL, f"Bottom face X: expected {length}, got {bot_bb.xlen}"
        assert abs(bot_bb.ylen - width_base) < TOL, f"Bottom face Y: expected {width_base}, got {bot_bb.ylen}"
    
        # Face count:
        # The left (X=-40) and right (X=+40) faces of base and top tier are coplanar
        # and merge into single faces spanning the full height.
        # Bottom(1) + base front/back(2) + merged left/right(2) + step ledges(2)
        # + top tier front/back(2) + top face(1) = 10
        n_faces = result.faces().size()
        assert n_faces == 10, f"Face count: expected 10, got {n_faces}"
    
        # All faces should be planar (no cylinders)
        n_planar = result.faces("%Plane").size()
        assert n_planar == n_faces, f"All faces should be planar: expected {n_faces}, got {n_planar}"
    
        # Verify the step ledge exists: horizontal faces at Z = extrude_h pointing upward
        step_faces = [f for f in result.faces().vals()
                      if abs(f.Center().z - extrude_h) < TOL and
                         abs(f.normalAt().z - 1.0) < TOL]
        assert len(step_faces) == 2, f"Step ledge faces at Z={extrude_h}: expected 2, got {len(step_faces)}"
    
        # Each step face spans full length in X, and (width_base - width_top)/2 in Y
        expected_step_y = (width_base - width_top) / 2
        for sf in step_faces:
            sf_bb = sf.BoundingBox()
            assert abs(sf_bb.xlen - length) < TOL, \
                f"Step face X span: expected {length}, got {sf_bb.xlen}"
            assert abs(sf_bb.ylen - expected_step_y) < TOL, \
                f"Step face Y span: expected {expected_step_y}, got {sf_bb.ylen}"
    
        # Verify the object is a single solid (not fragmented)
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00984833/gpt_generated.stl')
