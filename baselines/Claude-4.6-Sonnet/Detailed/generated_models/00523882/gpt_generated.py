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
        # First trapezoid (right trapezoid, right angles on left side)
        base1   = 1.11043
        top1    = 0.55953
        h1      = 0.625913
        width1  = 1.0011   # extrusion depth along Z
    
        # Second trapezoid
        base2   = 1.27908
        top2    = 0.619642
        h2      = 0.75
        width2  = 0.201835  # extrusion depth
    
        # --- Step 1: Build first trapezoid profile in XY plane ---
        # Right trapezoid: right angles at bottom-left and top-left (left side vertical)
        # Vertices: (0,0), (base1,0), (top1, h1), (0, h1)
        pts1 = [
            (0.0,   0.0),
            (base1, 0.0),
            (top1,  h1),
            (0.0,   h1),
        ]
    
        trap1 = (
            cq.Workplane("XY")
            .moveTo(pts1[0][0], pts1[0][1])
            .lineTo(pts1[1][0], pts1[1][1])
            .lineTo(pts1[2][0], pts1[2][1])
            .lineTo(pts1[3][0], pts1[3][1])
            .close()
            .extrude(width1)
        )
    
        # --- Step 2: Build second trapezoid profile ---
        # Right trapezoid with same orientation: right angles on left side
        # Vertices: (0,0), (base2,0), (top2, h2), (0, h2)
        pts2 = [
            (0.0,   0.0),
            (base2, 0.0),
            (top2,  h2),
            (0.0,   h2),
        ]
    
        trap2_raw = (
            cq.Workplane("XY")
            .moveTo(pts2[0][0], pts2[0][1])
            .lineTo(pts2[1][0], pts2[1][1])
            .lineTo(pts2[2][0], pts2[2][1])
            .lineTo(pts2[3][0], pts2[3][1])
            .close()
            .extrude(width2)
        )
    
        # --- Step 3: Position second trapezoid to attach to the side of the first ---
        # The first trapezoid occupies:
        #   X: [0, base1] (roughly), Y: [0, h1], Z: [0, width1]
        # We want to attach the second to the face at Z=0 of the first.
        # The second trapezoid is currently extruded along +Z (Z: [0, width2]).
        # We need to rotate it 180° about X axis so it extrudes in -Z direction,
        # then translate so its base aligns with the first's base at Z=0.
        #
        # After rotating 180° about X: Y -> -Y, Z -> -Z
        # The profile was in XY (Z=0 to Z=width2), after rotation it's in X(-Y) plane,
        # Z: [0, -width2]
        #
        # Better approach: rotate the second trapezoid so it lies on the face at Z=0
        # of the first trapezoid, extending in the -Z direction.
        #
        # Strategy: 
        # - The second trapezoid profile should be in the XY plane (same as first's cross-section)
        # - Extrude it in -Z direction (i.e., rotate 180° about X axis after extrusion)
        # - Translate to align bases: center the second's base with the first's base
        #
        # The first trapezoid's base is along Y=0, X=[0, base1], at Z=0
        # The second trapezoid's base is along Y=0, X=[0, base2]
        # Center alignment: shift second by (base1 - base2)/2 in X, keep Y=0
        # After 180° rotation about X: Y stays 0 (bottom), Z goes negative
        # We need to shift Z so the second's face at Z=0 aligns with first's face at Z=0
    
        # Get the solid from trap2_raw
        trap2_solid = trap2_raw.val()
    
        # Rotate 180° about X axis (through origin): (x,y,z) -> (x,-y,-z)
        # Then translate: x_offset = (base1 - base2)/2, y_offset = 0, z_offset = 0
        # After rotation, the profile (originally at Y=[0,h2]) maps to Y=[0,-h2]
        # and Z=[0,width2] maps to Z=[0,-width2]
        # We want the profile to align with first's profile at Z=0 face
        # First's profile at Z=0: Y=[0, h1], X=[0, base1]
        # After rotation, second's profile: Y=[0,-h2] — this goes downward, not aligned
    
        # Better: rotate 180° about Z axis instead, then flip
        # Let's think differently:
        # Attach to the face at Z=0, with the second extending in -Z direction
        # The second's cross-section should match the XY plane profile
        # So: keep the profile in XY, but extrude in -Z
        # 
        # Build trap2 extruded in -Z direction directly:
        trap2 = (
            cq.Workplane("XY")
            .moveTo(pts2[0][0], pts2[0][1])
            .lineTo(pts2[1][0], pts2[1][1])
            .lineTo(pts2[2][0], pts2[2][1])
            .lineTo(pts2[3][0], pts2[3][1])
            .close()
            .extrude(-width2)  # extrude in -Z direction
        )
    
        # Now translate to align with first trapezoid at Z=0 face
        # Center the second's base with the first's base in X
        x_offset = (base1 - base2) / 2.0
        y_offset = 0.0
        z_offset = 0.0  # both share Z=0 face
    
        trap2_positioned = trap2.translate((x_offset, y_offset, z_offset))
    
        # --- Step 4: Combine the two trapezoids ---
        result = trap1.union(trap2_positioned)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X extent: second trapezoid is centered relative to first
        # first: X=[0, base1=1.11043]
        # second: X=[x_offset, x_offset+base2] = [(1.11043-1.27908)/2, (1.11043-1.27908)/2 + 1.27908]
        x_off = (base1 - base2) / 2.0  # negative: -0.084325
        expected_xmin = min(0.0, x_off)
        expected_xmax = max(base1, x_off + base2)
        assert abs(bb.xmin - expected_xmin) < TOL, f"xmin: expected {expected_xmin:.4f}, got {bb.xmin:.4f}"
        assert abs(bb.xmax - expected_xmax) < TOL, f"xmax: expected {expected_xmax:.4f}, got {bb.xmax:.4f}"
    
        # Y extent: both trapezoids start at Y=0
        # first goes to h1=0.625913, second goes to h2=0.75
        expected_ymin = 0.0
        expected_ymax = max(h1, h2)  # 0.75
        assert abs(bb.ymin - expected_ymin) < TOL, f"ymin: expected {expected_ymin:.4f}, got {bb.ymin:.4f}"
        assert abs(bb.ymax - expected_ymax) < TOL, f"ymax: expected {expected_ymax:.4f}, got {bb.ymax:.4f}"
    
        # Z extent: first goes [0, width1=1.0011], second goes [0, -width2=-0.201835]
        expected_zmin = -width2   # -0.201835
        expected_zmax = width1    # 1.0011
        assert abs(bb.zmin - expected_zmin) < TOL, f"zmin: expected {expected_zmin:.4f}, got {bb.zmin:.4f}"
        assert abs(bb.zmax - expected_zmax) < TOL, f"zmax: expected {expected_zmax:.4f}, got {bb.zmax:.4f}"
    
        # Volume check: sum of individual volumes (they share a face at Z=0, no overlap in volume)
        vol1 = 0.5 * (base1 + top1) * h1 * width1
        vol2 = 0.5 * (base2 + top2) * h2 * width2
        expected_vol = vol1 + vol2
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.4f}, got {actual_vol:.4f}"
    
        # Check we have a single solid (union)
        assert result.solids().size() >= 1, "Expected at least one solid"
    
        # Check cylindrical faces count = 0 (no holes)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # Check the model has planar faces only
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 8, f"Expected at least 8 planar faces, got {planar_faces}"
    
        print(f"Bounding box: X=[{bb.xmin:.4f}, {bb.xmax:.4f}], Y=[{bb.ymin:.4f}, {bb.ymax:.4f}], Z=[{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"Volume: {actual_vol:.4f} (expected ~{expected_vol:.4f})")
        print(f"Planar faces: {planar_faces}")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00523882/gpt_generated.stl')
