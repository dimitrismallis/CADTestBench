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
        # --- Step 1: Define irregular pentagon vertices ---
        # Bottom edge (shortest): P0 to P1, length = 3
        # Pentagon is irregular with varying edge lengths
        # Height of pentagon (Y extent) = 7
        # Extrusion = ~1.9 * 7 = 13.3
    
        P0 = (-1.5, 0.0)   # bottom-left of shortest edge
        P1 = ( 1.5, 0.0)   # bottom-right of shortest edge
        P2 = ( 4.5, 3.5)   # right
        P3 = ( 1.5, 7.0)   # top-right
        P4 = (-3.0, 5.0)   # top-left
    
        vertices = [P0, P1, P2, P3, P4]
    
        # Compute edge lengths for reference
        def edge_len(a, b):
            return math.sqrt((b[0]-a[0])**2 + (b[1]-a[1])**2)
    
        edges_lengths = [
            edge_len(P0, P1),  # bottom (shortest)
            edge_len(P1, P2),
            edge_len(P2, P3),
            edge_len(P3, P4),
            edge_len(P4, P0),
        ]
        print("Edge lengths:", [f"{l:.3f}" for l in edges_lengths])
        assert edges_lengths[0] == min(edges_lengths), \
            f"Bottom edge is not shortest: {edges_lengths}"
    
        # Pentagon height (Y extent)
        ys = [v[1] for v in vertices]
        penta_height = max(ys) - min(ys)
        print(f"Pentagon height: {penta_height}")
    
        # Extrusion depth: almost 2x the pentagon height
        extrude_depth = round(1.9 * penta_height, 2)
        print(f"Extrusion depth: {extrude_depth}")
    
        # --- Step 2: Build the pentagon wire and extrude ---
        # Use the Workplane wire-drawing API
        result = (
            cq.Workplane("XY")
            .moveTo(P0[0], P0[1])
            .lineTo(P1[0], P1[1])
            .lineTo(P2[0], P2[1])
            .lineTo(P3[0], P3[1])
            .lineTo(P4[0], P4[1])
            .close()
            .extrude(extrude_depth)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        # X: from -3.0 to 4.5 → xlen = 7.5
        expected_xlen = 4.5 - (-3.0)
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X extent: expected {expected_xlen}, got {bb.xlen}"
    
        # Y: from 0 to 7.0 → ylen = 7.0
        expected_ylen = 7.0 - 0.0
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y extent: expected {expected_ylen}, got {bb.ylen}"
    
        # Z: extrusion depth
        assert abs(bb.zlen - extrude_depth) < TOL, \
            f"Z extent (extrusion): expected {extrude_depth}, got {bb.zlen}"
    
        # Extrusion is almost 2x pentagon height (between 1.7x and 2.0x)
        ratio = bb.zlen / penta_height
        assert 1.7 < ratio < 2.0, \
            f"Extrusion ratio to pentagon height: expected ~1.9, got {ratio:.3f}"
    
        # Face count: pentagonal prism has 2 pentagonal faces + 5 rectangular side faces = 7
        face_count = result.faces().size()
        assert face_count == 7, \
            f"Face count: expected 7, got {face_count}"
    
        # Edge count: 5 (bottom pentagon) + 5 (top pentagon) + 5 (vertical) = 15
        edge_count = result.edges().size()
        assert edge_count == 15, \
            f"Edge count: expected 15, got {edge_count}"
    
        # Vertex count: 5 (bottom) + 5 (top) = 10
        vertex_count = result.vertices().size()
        assert vertex_count == 10, \
            f"Vertex count: expected 10, got {vertex_count}"
    
        # Volume: area of pentagon * extrusion depth
        # Compute pentagon area using shoelace formula
        n = len(vertices)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i][0] * vertices[j][1]
            area -= vertices[j][0] * vertices[i][1]
        penta_area = abs(area) / 2.0
        print(f"Pentagon area: {penta_area}")
    
        expected_vol = penta_area * extrude_depth
        actual_vol = solid.Volume()
        print(f"Expected volume: {expected_vol:.3f}, Actual volume: {actual_vol:.3f}")
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Bottom edge is shortest: verify by checking the bottom face edges
        # The bottom face is at Z=0, top face at Z=extrude_depth
        # Check that the 2 planar end faces exist
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 7, \
            f"All faces should be planar for a prism: expected 7, got {planar_faces}"
    
        # Confirm bottom edge (shortest) length = 3.0
        bottom_edge_len = edge_len(P0, P1)
        assert abs(bottom_edge_len - 3.0) < TOL, \
            f"Bottom edge length: expected 3.0, got {bottom_edge_len}"
    
        # Confirm it's the shortest edge
        assert bottom_edge_len < min(edges_lengths[1:]), \
            f"Bottom edge {bottom_edge_len:.3f} is not shorter than all others: {edges_lengths[1:]}"
    
        print("All assertions passed!")
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00998398/gpt_generated.stl')
