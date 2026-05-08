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
        base = 60.0       # base of right-angled triangle
        height = 130.0    # height > 2 * base
        thickness = 10.0  # extrusion depth (rack thickness)
        wall = 5.0        # wall thickness of the hollow frame
    
        # --- Step 1: Define outer triangle vertices (right angle at origin) ---
        # Bottom-left (right angle), Bottom-right, Top-left
        v0 = (0.0, 0.0)
        v1 = (base, 0.0)
        v2 = (0.0, height)
    
        # --- Step 2: Compute inner triangle by offsetting each edge inward ---
        # For a right-angled triangle, inset each side by `wall` distance.
        # The inset vertices are computed by moving inward along the angle bisectors.
    
        # Edge vectors (normalized)
        def norm(p, q):
            dx, dy = q[0]-p[0], q[1]-p[1]
            L = math.sqrt(dx*dx + dy*dy)
            return dx/L, dy/L
    
        def inward_normal(p, q):
            # 90° CCW rotation of edge direction gives inward normal for CCW winding
            dx, dy = norm(p, q)
            return -dy, dx  # perpendicular pointing inward (for CCW triangle)
    
        # Our triangle v0->v1->v2 is CCW? Let's check:
        # v0=(0,0), v1=(60,0), v2=(0,130)
        # Cross product (v1-v0) x (v2-v0) = (60,0) x (0,130) = 60*130 - 0*0 = 7800 > 0 → CCW ✓
    
        # Inward normals for each edge
        n01 = inward_normal(v0, v1)  # bottom edge: normal points up (+Y)
        n12 = inward_normal(v1, v2)  # hypotenuse: normal points inward
        n20 = inward_normal(v2, v0)  # left edge: normal points right (+X)
    
        # Offset each edge inward by `wall`
        # Offset line: point on edge + wall * inward_normal
        # Intersection of two offset lines gives inner vertex
    
        def line_intersect(p1, d1, p2, d2):
            # Solve p1 + t*d1 = p2 + s*d2
            # t*d1x - s*d2x = p2x - p1x
            # t*d1y - s*d2y = p2y - p1y
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            denom = d1[0]*(-d2[1]) - d1[1]*(-d2[0])
            if abs(denom) < 1e-10:
                return None
            t = (dx*(-d2[1]) - dy*(-d2[0])) / denom
            return (p1[0] + t*d1[0], p1[1] + t*d1[1])
    
        # Offset points on each edge
        op01 = (v0[0] + wall*n01[0], v0[1] + wall*n01[1])
        op12 = (v1[0] + wall*n12[0], v1[1] + wall*n12[1])
        op20 = (v2[0] + wall*n20[0], v2[1] + wall*n20[1])
    
        # Edge directions
        d01 = norm(v0, v1)
        d12 = norm(v1, v2)
        d20 = norm(v2, v0)
    
        # Inner vertices: intersection of adjacent offset edges
        iv0 = line_intersect(op01, d01, op20, d20)  # near v0
        iv1 = line_intersect(op01, d01, op12, d12)  # near v1
        iv2 = line_intersect(op12, d12, op20, d20)  # near v2
    
        print(f"Outer vertices: {v0}, {v1}, {v2}")
        print(f"Inner vertices: {iv0}, {iv1}, {iv2}")
    
        # --- Step 3: Build the hollow triangle sketch using Workplane ---
        # Create outer triangle wire and inner triangle wire, then extrude the annular region
    
        # Build outer profile as a closed wire
        outer = (
            cq.Workplane("XY")
            .moveTo(v0[0], v0[1])
            .lineTo(v1[0], v1[1])
            .lineTo(v2[0], v2[1])
            .close()
        )
    
        # Build inner profile as a closed wire (hole)
        inner = (
            cq.Workplane("XY")
            .moveTo(iv0[0], iv0[1])
            .lineTo(iv1[0], iv1[1])
            .lineTo(iv2[0], iv2[1])
            .close()
        )
    
        # --- Step 4: Extrude outer triangle and cut inner triangle ---
        outer_solid = outer.extrude(thickness)
        inner_solid = inner.extrude(thickness)
    
        result = outer_solid.cut(inner_solid)
    
        # --- Final object verification ---
        TOL = 0.5  # tolerance for floating point
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - base) < TOL, f"X length: expected {base}, got {bb.xlen}"
        assert abs(bb.ylen - height) < TOL, f"Y length: expected {height}, got {bb.ylen}"
        assert abs(bb.zlen - thickness) < TOL, f"Z length: expected {thickness}, got {bb.zlen}"
    
        # Height > 2 * base
        assert height > 2 * base, f"Height {height} should be > 2 * base {2*base}"
    
        # Volume check: outer triangle area - inner triangle area, times thickness
        def tri_area(a, b, c):
            return 0.5 * abs((b[0]-a[0])*(c[1]-a[1]) - (c[0]-a[0])*(b[1]-a[1]))
    
        outer_area = tri_area(v0, v1, v2)
        inner_area = tri_area(iv0, iv1, iv2)
        expected_vol = (outer_area - inner_area) * thickness
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Face count: hollow extruded triangle has:
        # 2 triangular faces (top + bottom) × 2 (outer + inner) = 4 triangular faces
        # 3 outer rectangular side faces + 3 inner rectangular side faces = 6 rectangular faces
        # Total = 10 faces (but corners may merge — check at least planar faces exist)
        face_count = result.faces().size()
        print(f"Face count: {face_count}")
        assert face_count >= 8, f"Expected at least 8 faces, got {face_count}"
    
        # Check it has planar faces only (no cylinders)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # Check top and bottom faces exist
        top_faces = result.faces(">Z").size()
        bot_faces = result.faces("<Z").size()
        assert top_faces >= 1, f"Expected top face(s), got {top_faces}"
        assert bot_faces >= 1, f"Expected bottom face(s), got {bot_faces}"
    
        # Check the shape is a single solid
        solid_count = result.solids().size()
        assert solid_count == 1, f"Expected 1 solid, got {solid_count}"
    
        # Check center of mass is inside the bounding box
        com = cq.Shape.centerOfMass(result.val())
        assert bb.xmin < com.x < bb.xmax, f"COM x={com.x} outside [{bb.xmin}, {bb.xmax}]"
        assert bb.ymin < com.y < bb.ymax, f"COM y={com.y} outside [{bb.ymin}, {bb.ymax}]"
        assert abs(com.z - thickness/2) < TOL, f"COM z={com.z} expected ~{thickness/2}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
        print(f"Center of mass: ({com.x:.2f}, {com.y:.2f}, {com.z:.2f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00980412/gpt_generated.stl')
