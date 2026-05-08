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
        base = 0.037173
        height = 0.759401
        thickness = 0.015931  # extrusion thickness
        wall = 0.003          # wall thickness for hollow frame
    
        # --- Step 1: Define outer triangle vertices (CCW order) ---
        # Right angle at origin, base along X, height along Y
        # p0=(0,0), p1=(base,0), p2=(0,height) is CCW
        p0 = (0.0, 0.0)       # right angle corner
        p1 = (base, 0.0)      # base end
        p2 = (0.0, height)    # height end
    
        hyp = math.sqrt(base**2 + height**2)
    
        # --- Step 2: Compute inner triangle using correct inward normals ---
        # For a CCW polygon, inward normal of edge A->B is obtained by rotating
        # the edge direction (B-A)/|B-A| by -90° (clockwise): (dy, -dx) -> wait
        # Edge direction (dx, dy), left normal = (-dy, dx), right normal = (dy, -dx)
        # For CCW polygon, interior is to the LEFT, so inward normal = left normal = (-dy, dx)
    
        # Edge p0->p1: direction (1, 0), inward normal = (0, 1)  [pointing up, into triangle] ✓
        # Edge p1->p2: direction (-base/hyp, height/hyp), inward normal = (-height/hyp, -base/hyp) [pointing toward origin] ✓
        # Edge p2->p0: direction (0, -1), inward normal = (1, 0)  [pointing right, into triangle] ✓
    
        # Inward normals at each edge:
        n_p0p1 = (0.0, 1.0)                          # bottom edge
        n_p1p2 = (-height/hyp, -base/hyp)            # hypotenuse
        n_p2p0 = (1.0, 0.0)                          # left edge
    
        # --- Inset vertex ip0 (at right-angle corner, between edges p2p0 and p0p1) ---
        # Edges meeting at p0: incoming p2->p0 (normal n_p2p0) and outgoing p0->p1 (normal n_p0p1)
        # For right angle (90°), bisector of inward normals:
        bis0 = (n_p2p0[0] + n_p0p1[0], n_p2p0[1] + n_p0p1[1])
        bis0_len = math.sqrt(bis0[0]**2 + bis0[1]**2)
        bis0 = (bis0[0]/bis0_len, bis0[1]/bis0_len)
        # Angle at p0 = 90°, so sin(half_angle) = sin(45°) = sqrt(2)/2
        angle_p0 = math.pi / 2.0
        d0 = wall / math.sin(angle_p0 / 2.0)
        ip0 = (p0[0] + bis0[0]*d0, p0[1] + bis0[1]*d0)
    
        # --- Inset vertex ip1 (at base end, between edges p0p1 and p1p2) ---
        bis1 = (n_p0p1[0] + n_p1p2[0], n_p0p1[1] + n_p1p2[1])
        bis1_len = math.sqrt(bis1[0]**2 + bis1[1]**2)
        bis1 = (bis1[0]/bis1_len, bis1[1]/bis1_len)
        # Angle at p1:
        e_in_p1 = (1.0, 0.0)           # direction of incoming edge p0->p1
        e_out_p1 = (-base/hyp, height/hyp)  # direction of outgoing edge p1->p2
        cos_a1 = e_in_p1[0]*e_out_p1[0] + e_in_p1[1]*e_out_p1[1]
        angle_p1 = math.acos(max(-1.0, min(1.0, cos_a1)))
        # Interior angle = pi - angle between edge directions (exterior angle)
        interior_angle_p1 = math.pi - angle_p1
        d1 = wall / math.sin(interior_angle_p1 / 2.0)
        ip1 = (p1[0] + bis1[0]*d1, p1[1] + bis1[1]*d1)
    
        # --- Inset vertex ip2 (at height end, between edges p1p2 and p2p0) ---
        bis2 = (n_p1p2[0] + n_p2p0[0], n_p1p2[1] + n_p2p0[1])
        bis2_len = math.sqrt(bis2[0]**2 + bis2[1]**2)
        bis2 = (bis2[0]/bis2_len, bis2[1]/bis2_len)
        e_in_p2 = (-base/hyp, height/hyp)   # direction of incoming edge p1->p2
        e_out_p2 = (0.0, -1.0)              # direction of outgoing edge p2->p0
        cos_a2 = e_in_p2[0]*e_out_p2[0] + e_in_p2[1]*e_out_p2[1]
        angle_p2 = math.acos(max(-1.0, min(1.0, cos_a2)))
        interior_angle_p2 = math.pi - angle_p2
        d2 = wall / math.sin(interior_angle_p2 / 2.0)
        ip2 = (p2[0] + bis2[0]*d2, p2[1] + bis2[1]*d2)
    
        print(f"Outer: {p0}, {p1}, {p2}")
        print(f"Inner: {ip0}, {ip1}, {ip2}")
        print(f"Angles at p0={math.degrees(angle_p0):.1f}, p1={math.degrees(interior_angle_p1):.1f}, p2={math.degrees(interior_angle_p2):.1f}")
    
        # --- Step 3: Build the hollow triangle profile using Sketch API ---
        sketch = (
            cq.Sketch()
            .polygon([p0, p1, p2], mode="a")
            .reset()
            .polygon([ip0, ip1, ip2], mode="s")
        )
    
        # --- Step 4: Extrude to thickness ---
        result = cq.Workplane("XY").placeSketch(sketch).extrude(thickness)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - base) < TOL, f"X length: expected {base}, got {bb.xlen}"
        assert abs(bb.ylen - height) < TOL, f"Y length: expected {height}, got {bb.ylen}"
        assert abs(bb.zlen - thickness) < TOL, f"Z thickness: expected {thickness}, got {bb.zlen}"
    
        # Height > 2 * base check
        assert height > 2 * base, f"Height {height} should be > 2 * base {2*base}"
    
        # Volume check: hollow triangle frame
        outer_area = 0.5 * base * height
        # Inner triangle area using shoelace formula
        inner_area = 0.5 * abs(
            ip0[0]*(ip1[1] - ip2[1]) +
            ip1[0]*(ip2[1] - ip0[1]) +
            ip2[0]*(ip0[1] - ip1[1])
        )
        print(f"Outer area: {outer_area:.8f}, Inner area: {inner_area:.8f}")
        expected_vol = (outer_area - inner_area) * thickness
        print(f"Expected volume: {expected_vol:.8f}")
        actual_vol = result.val().Volume()
        print(f"Actual volume:   {actual_vol:.8f}")
    
        assert actual_vol > 0, "Volume should be positive"
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.8f}, got {actual_vol:.8f}"
    
        # Check bounding box origin is near (0,0,0)
        assert abs(bb.xmin) < TOL, f"xmin should be ~0, got {bb.xmin}"
        assert abs(bb.ymin) < TOL, f"ymin should be ~0, got {bb.ymin}"
        assert abs(bb.zmin) < TOL, f"zmin should be ~0, got {bb.zmin}"
    
        # Check face count: hollow extruded triangle has
        # 2 annular triangular faces (top/bottom) + 3 outer side faces + 3 inner side faces = 8 faces
        face_count = result.faces().size()
        assert face_count == 8, f"Face count: expected 8, got {face_count}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.6f} x {bb.ylen:.6f} x {bb.zlen:.6f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00980412/gpt_generated.stl')
