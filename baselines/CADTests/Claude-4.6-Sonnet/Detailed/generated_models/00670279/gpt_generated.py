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
        height = 0.26068          # height of the ring (extrusion length along Y)
        outer_diameter = 1.5      # outer diameter
        outer_radius = outer_diameter / 2.0   # 0.75
        reduction = 0.013033      # reduction from both sides
        inner_diameter = outer_diameter - 2 * reduction  # 1.5 - 2*0.013033 = 1.473934
        inner_radius = inner_diameter / 2.0              # 0.736967
    
        # --- Step 1: Create annular (ring) profile in XZ plane ---
        # The ring is extruded along Y-axis, so the cross-section lies in the XZ plane.
        # We use the "XZ" workplane and create two concentric circles, then extrude along Y.
    
        # Create outer circle profile on XZ plane
        outer_circle = cq.Workplane("XZ").circle(outer_radius)
        # Create inner circle (hole) profile
        inner_circle = cq.Workplane("XZ").circle(inner_radius)
    
        # --- Step 2: Extrude the annular profile along Y-axis ---
        # Extrude outer circle and subtract inner circle to form the ring
        result = (
            cq.Workplane("XZ")
            .circle(outer_radius)
            .extrude(height / 2.0, both=True)   # extrude symmetrically along Y
        )
    
        # Subtract inner cylinder to create the hole
        inner_cyl = (
            cq.Workplane("XZ")
            .circle(inner_radius)
            .extrude(height / 2.0, both=True)
        )
    
        result = result.cut(inner_cyl)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        # X extent: outer diameter = 1.5
        assert abs(bb.xlen - outer_diameter) < TOL, \
            f"X extent: expected {outer_diameter}, got {bb.xlen}"
    
        # Z extent: outer diameter = 1.5 (ring cross-section in XZ plane)
        assert abs(bb.zlen - outer_diameter) < TOL, \
            f"Z extent: expected {outer_diameter}, got {bb.zlen}"
    
        # Y extent: height = 0.26068 (extrusion along Y)
        assert abs(bb.ylen - height) < TOL, \
            f"Y extent: expected {height}, got {bb.ylen}"
    
        # Volume check: annular cylinder volume = pi * (R_outer^2 - R_inner^2) * height
        expected_vol = math.pi * (outer_radius**2 - inner_radius**2) * height
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical faces exist (inner and outer curved surfaces)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 2, \
            f"Expected at least 2 cylindrical faces (inner + outer), got {cyl_faces}"
    
        # Check planar faces (top and bottom flat annular faces)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 2, \
            f"Expected at least 2 planar faces (two annular ends), got {planar_faces}"
    
        # Check center of mass is at origin (symmetric extrusion)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"Center of mass Z: expected 0, got {com.z}"
    
        # Check that a point inside the wall is inside the solid
        mid_radius = (outer_radius + inner_radius) / 2.0
        assert result.val().isInside((mid_radius, 0, 0)), \
            f"Point at mid-wall radius ({mid_radius}, 0, 0) should be inside the solid"
    
        # Check that a point in the hole is NOT inside the solid
        assert not result.val().isInside((0, 0, 0)), \
            "Center point (0,0,0) should be outside the solid (inside the hole)"
    
        # Check that a point outside the ring is NOT inside the solid
        assert not result.val().isInside((outer_radius + 0.1, 0, 0)), \
            f"Point outside ring should not be inside the solid"
    
        print(f"All assertions passed!")
        print(f"Outer diameter: {outer_diameter}, Inner diameter: {inner_diameter:.6f}")
        print(f"Height (Y-axis): {height}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Bounding box: X={bb.xlen:.5f}, Y={bb.ylen:.5f}, Z={bb.zlen:.5f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00670279/gpt_generated.stl')
