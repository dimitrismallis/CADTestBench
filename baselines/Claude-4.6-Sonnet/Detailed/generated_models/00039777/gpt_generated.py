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
        L = 0.725228       # length
        H = 0.103604       # extrusion height
    
        # --- Step 1: Define vertices of the pentagon-like shape ---
        # The shape is drawn in the XY plane
        v0 = (0, 0)
        v1 = (L, 0)
        v2 = (0.932436, L/4 + 0.0155)
        v3 = (1.05676, L/2)
        v4 = (0.932436, L - (L/4 + 0.0155))
        v5 = (L, L)
        v6 = (0, L)
    
        vertices = [v0, v1, v2, v3, v4, v5, v6]
    
        # --- Step 2: Build the closed 2D profile using lineTo ---
        profile = (
            cq.Workplane("XY")
            .moveTo(v0[0], v0[1])
            .lineTo(v1[0], v1[1])
            .lineTo(v2[0], v2[1])
            .lineTo(v3[0], v3[1])
            .lineTo(v4[0], v4[1])
            .lineTo(v5[0], v5[1])
            .lineTo(v6[0], v6[1])
            .close()
        )
    
        # --- Step 3: Extrude to height H ---
        result = profile.extrude(H)
    
        # --- Step 4: Rotate and translate for proper orientation ---
        # Rotate 90 degrees around X axis so the shape stands upright
        # (Y becomes Z, Z becomes -Y)
        # Then translate so the bottom sits on Z=0
        result = result.rotate((0, 0, 0), (1, 0, 0), -90)
        # After rotation: the shape's Y extent (0 to L) maps to Z (0 to -L)
        # Translate to bring it back to positive Z
        result = result.translate((0, 0, L))
    
        # --- Final object verification ---
        TOL = 0.001
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Check bounding box dimensions
        # After rotation and translation:
        # X: 0 to 1.05676 (the extended x of the shape)
        # Y: 0 to H (the extrusion, now along Y)
        # Z: 0 to L (the original Y extent)
    
        print(f"BBox: x=[{bb.xmin:.4f}, {bb.xmax:.4f}], y=[{bb.ymin:.4f}, {bb.ymax:.4f}], z=[{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"xlen={bb.xlen:.6f}, ylen={bb.ylen:.6f}, zlen={bb.zlen:.6f}")
    
        # X extent: 0 to 1.05676
        assert abs(bb.xmin) < TOL, f"xmin expected ~0, got {bb.xmin}"
        assert abs(bb.xmax - 1.05676) < TOL, f"xmax expected ~1.05676, got {bb.xmax}"
    
        # Y extent: 0 to H (extrusion thickness)
        assert abs(bb.ymin) < TOL, f"ymin expected ~0, got {bb.ymin}"
        assert abs(bb.ymax - H) < TOL, f"ymax expected ~{H}, got {bb.ymax}"
    
        # Z extent: 0 to L
        assert abs(bb.zmin) < TOL, f"zmin expected ~0, got {bb.zmin}"
        assert abs(bb.zmax - L) < TOL, f"zmax expected ~{L}, got {bb.zmax}"
    
        # Check volume: area of polygon * H
        # Compute polygon area using shoelace formula
        verts = [v0, v1, v2, v3, v4, v5, v6]
        n = len(verts)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += verts[i][0] * verts[j][1]
            area -= verts[j][0] * verts[i][1]
        area = abs(area) / 2.0
        expected_vol = area * H
        actual_vol = solid.Volume()
        print(f"Polygon area: {area:.6f}, Expected volume: {expected_vol:.6f}, Actual volume: {actual_vol:.6f}")
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check face count: 7 side faces + 2 end faces = 9 total
        face_count = result.faces().size()
        print(f"Face count: {face_count}")
        assert face_count == 9, f"Expected 9 faces, got {face_count}"
    
        # Check edge count: 7 edges on each end face + 7 side edges = 7+7+7 = 21
        edge_count = result.edges().size()
        print(f"Edge count: {edge_count}")
        assert edge_count == 21, f"Expected 21 edges, got {edge_count}"
    
        # Check vertex count: 7 vertices * 2 = 14
        vertex_count = result.vertices().size()
        print(f"Vertex count: {vertex_count}")
        assert vertex_count == 14, f"Expected 14 vertices, got {vertex_count}"
    
        # Check the extrusion height (Y direction)
        assert abs(bb.ylen - H) < TOL, f"Extrusion height: expected {H}, got {bb.ylen}"
    
        # Check the length (Z direction after rotation)
        assert abs(bb.zlen - L) < TOL, f"Length: expected {L}, got {bb.zlen}"
    
        # Check symmetry: center of mass should be symmetric in Z around L/2
        com = cq.Shape.centerOfMass(solid)
        print(f"Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
        assert abs(com.z - L/2) < TOL, f"COM Z should be ~{L/2:.4f}, got {com.z:.4f}"
        assert abs(com.y - H/2) < TOL, f"COM Y should be ~{H/2:.4f}, got {com.y:.4f}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00039777/gpt_generated.stl')
