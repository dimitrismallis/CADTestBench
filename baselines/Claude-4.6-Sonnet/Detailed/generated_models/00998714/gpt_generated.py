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
        s = 0.929516          # side length
        h = s * math.sqrt(3) / 2  # triangle height ≈ 0.805000
        r = 0.619677 / 2     # semicircle radius ≈ 0.309839
        extrude_h = 0.3
    
        # Triangle pointing DOWN: apex at bottom, flat edge at top.
        # Place apex at (0, 0), top edge at y = h.
        # Top-left: (-s/2, h), Top-right: (s/2, h), Apex: (0, 0)
        # After cut, the semicircle removes the apex region.
        # The diameter of the semicircle is horizontal at y=0 (the apex level).
        # The semicircle curves upward (into the triangle) with radius r.
        # After cut: ymin = 0 (diameter endpoints at y=0), ymax = h.
    
        y_apex = 0.0
        y_top  = h          # ≈ 0.80500
    
        # --- Step 1: Create the equilateral triangle extruded solid ---
        triangle = (
            cq.Workplane("XY")
            .moveTo(-s/2, y_top)
            .lineTo( s/2, y_top)
            .lineTo(0.0,  y_apex)
            .close()
            .extrude(extrude_h)
        )
    
        # --- Step 2: Create a full cylinder at the apex for boolean cut ---
        # Cylinder centered at apex (0, 0), radius r.
        # The upper half (y > 0) is inside the triangle → this is the semicircle to remove.
        # The lower half (y < 0) is outside the triangle → cut has no effect there.
        cutter = (
            cq.Workplane("XY")
            .moveTo(0.0, y_apex)
            .circle(r)
            .extrude(extrude_h)
        )
    
        # --- Step 3: Subtract the cylinder from the triangle ---
        result = triangle.cut(cutter)
    
        # --- Debug info ---
        bb = result.val().BoundingBox()
        actual_vol = result.val().Volume()
        tri_area = (math.sqrt(3) / 4) * s ** 2
        semi_area = math.pi * r ** 2 / 2
        profile_area = tri_area - semi_area
        expected_vol = profile_area * extrude_h
        print(f"Bounding box: xlen={bb.xlen:.5f}, ylen={bb.ylen:.5f}, zlen={bb.zlen:.5f}")
        print(f"  ymin={bb.ymin:.5f}, ymax={bb.ymax:.5f}")
        print(f"Actual volume: {actual_vol:.5f}, Expected: {expected_vol:.5f}")
        print(f"Face count: {result.faces().size()}")
        print(f"Cylindrical faces: {result.faces('%Cylinder').size()}")
    
        # --- Final object verification ---
        TOL = 0.01
    
        # X extent: from -s/2 to s/2
        assert abs(bb.xlen - s) < TOL, \
            f"X length: expected {s:.4f}, got {bb.xlen:.4f}"
    
        # Z extent (extrusion height)
        assert abs(bb.zlen - extrude_h) < TOL, \
            f"Z length (height): expected {extrude_h}, got {bb.zlen:.4f}"
    
        # Y extent:
        # - ymin = 0: the semicircle cut removes the apex, leaving flat edges at y=0
        # - ymax = h: the top edge of the triangle
        assert abs(bb.ymin - 0.0) < TOL, \
            f"Y min: expected 0.0 (apex cut away), got {bb.ymin:.4f}"
        assert abs(bb.ymax - y_top) < TOL, \
            f"Y max: expected {y_top:.4f}, got {bb.ymax:.4f}"
    
        # Volume: triangle minus semicircle (upper half of cylinder inside triangle), extruded by 0.3
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.5f}, got {actual_vol:.5f}"
    
        # Cylindrical face: 1 (from the semicircle cutout)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Symmetry: center of mass X should be ~0
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X should be ~0, got {com.x:.4f}"
    
        # The object should contain a point well inside the triangle but above the semicircle
        inside_pt = (0.0, h * 0.8, extrude_h / 2)
        assert result.val().isInside(inside_pt), \
            f"Point {inside_pt} should be inside the solid"
    
        # The apex point (0, 0, extrude_h/2) should NOT be inside (it was cut away)
        apex_pt = (0.0, 0.0, extrude_h / 2)
        assert not result.val().isInside(apex_pt), \
            f"Apex point {apex_pt} should have been cut away"
    
        print("All assertions passed!")
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00998714/gpt_generated.stl')
