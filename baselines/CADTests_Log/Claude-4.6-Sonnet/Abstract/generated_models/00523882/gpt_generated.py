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
        # First right trapezoid profile (in XY plane)
        b1 = 30.0   # bottom length
        t1 = 20.0   # top length
        h1 = 25.0   # height of trapezoid
        e1 = 20.0   # extrude depth (along Z)
    
        # Second right trapezoid profile (slightly larger, much less extruded)
        b2 = 35.0   # bottom length (slightly larger)
        t2 = 25.0   # top length (slightly larger)
        h2 = 28.0   # height (slightly larger)
        e2 = 5.0    # extrude depth (substantially less than e1)
    
        # --- Step 1: Build first right trapezoid and extrude ---
        # Right trapezoid vertices: right angles at (0,0) and (0,h1)
        # Bottom: from (0,0) to (b1,0)
        # Right side (slanted): from (b1,0) to (t1,h1)
        # Top: from (t1,h1) to (0,h1)
        # Left side (vertical): from (0,h1) to (0,0)
        trap1 = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(b1, 0)
            .lineTo(t1, h1)
            .lineTo(0, h1)
            .close()
            .extrude(e1)
        )
    
        # --- Step 2: Build second right trapezoid and attach to back face of first ---
        # The second trapezoid is placed at Z=e1, extending further in +Z by e2.
        trap2 = (
            cq.Workplane("XY", origin=(0, 0, e1))
            .moveTo(0, 0)
            .lineTo(b2, 0)
            .lineTo(t2, h2)
            .lineTo(0, h2)
            .close()
            .extrude(e2)
        )
    
        # --- Step 3: Union the two shapes ---
        result = trap1.union(trap2)
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # X extent: max of b1 and b2 at bottom = b2 = 35 (since b2 > b1)
        assert bb.xmin < TOL, f"X min should be ~0, got {bb.xmin}"
        assert abs(bb.xmax - b2) < TOL, f"X max should be ~{b2}, got {bb.xmax}"
    
        # Y extent: max of h1 and h2 = h2 = 28
        assert bb.ymin < TOL, f"Y min should be ~0, got {bb.ymin}"
        assert abs(bb.ymax - h2) < TOL, f"Y max should be ~{h2}, got {bb.ymax}"
    
        # Z extent: e1 + e2 = 25
        assert bb.zmin < TOL, f"Z min should be ~0, got {bb.zmin}"
        assert abs(bb.zmax - (e1 + e2)) < TOL, f"Z max should be ~{e1+e2}, got {bb.zmax}"
    
        # Volume check:
        # Trap1 area = 0.5*(b1+t1)*h1 = 0.5*(30+20)*25 = 625; vol1 = 625*20 = 12500
        # Trap2 area = 0.5*(b2+t2)*h2 = 0.5*(35+25)*28 = 840; vol2 = 840*5 = 4200
        # They share no volume (attached face-to-face), total = 16700
        area1 = 0.5 * (b1 + t1) * h1
        vol1 = area1 * e1
        area2 = 0.5 * (b2 + t2) * h2
        vol2 = area2 * e2
        expected_vol = vol1 + vol2
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Check that the result is a single solid
        assert result.solids().size() == 1, \
            f"Expected 1 solid after union, got {result.solids().size()}"
    
        # Check extrude depths: second shape is substantially less extruded (e2=5 vs e1=20)
        assert e2 < e1 / 2, f"Second extrude {e2} should be substantially less than first {e1}"
    
        # Check second shape is slightly larger: b2 > b1 and h2 > h1
        assert b2 > b1, f"Second trapezoid bottom {b2} should be larger than first {b1}"
        assert h2 > h1, f"Second trapezoid height {h2} should be larger than first {h1}"
    
        # Check planar faces exist (trapezoid has planar faces)
        planar_count = result.faces("%Plane").size()
        assert planar_count >= 6, f"Expected at least 6 planar faces, got {planar_count}"
    
        # Verify the center of mass Z is between 0 and total Z extent,
        # and closer to the first shape's centroid (Z=e1/2=10) than to the
        # second shape's centroid (Z=e1+e2/2=22.5), meaning COM Z < midpoint of the two centroids
        centroid1_z = e1 / 2.0          # = 10.0
        centroid2_z = e1 + e2 / 2.0     # = 22.5
        midpoint_centroids_z = (vol1 * centroid1_z + vol2 * centroid2_z) / (vol1 + vol2)
        com = cq.Shape.centerOfMass(result.val())
        assert 0 < com.z < (e1 + e2), \
            f"COM Z {com.z:.2f} should be within total Z range [0, {e1+e2}]"
        # The first shape has much larger volume, so COM Z should be closer to centroid1_z
        assert abs(com.z - centroid1_z) < abs(com.z - centroid2_z), \
            f"COM Z {com.z:.2f} should be closer to first shape centroid ({centroid1_z}) than second ({centroid2_z})"
    
        print(f"Bounding box: X={bb.xlen:.2f}, Y={bb.ylen:.2f}, Z={bb.zlen:.2f}")
        print(f"Volume: expected={expected_vol:.1f}, actual={actual_vol:.1f}")
        print(f"Planar faces: {planar_count}")
        print(f"Center of mass: ({com.x:.2f}, {com.y:.2f}, {com.z:.2f})")
        print(f"Centroid Z check: COM={com.z:.2f}, shape1_centroid={centroid1_z}, shape2_centroid={centroid2_z}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00523882/gpt_generated.stl')
