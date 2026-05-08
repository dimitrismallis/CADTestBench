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
        base_len   = 1.49593
        top_len    = 0.910569
        trap_h     = 0.382114
        x_shift    = 0.026423
        extrude_w  = 0.589754
    
        # --- Step 1: Define trapezoid vertices (centered + x_shift) ---
        # Isosceles trapezoid centered at x_shift, base at z=0, top at z=trap_h
        bx = base_len / 2.0
        tx = top_len  / 2.0
    
        # Vertices in XZ plane (will extrude along Y)
        # Bottom-left, Bottom-right, Top-right, Top-left
        v0 = (-bx + x_shift, 0.0)          # bottom-left
        v1 = ( bx + x_shift, 0.0)          # bottom-right
        v2 = ( tx + x_shift, trap_h)       # top-right
        v3 = (-tx + x_shift, trap_h)       # top-left
    
        # --- Step 2: Build the trapezoidal profile on XZ plane ---
        # Use XZ plane so extrusion goes along Y axis
        result = (
            cq.Workplane("XZ")
            .moveTo(v0[0], v0[1])
            .lineTo(v1[0], v1[1])
            .lineTo(v2[0], v2[1])
            .lineTo(v3[0], v3[1])
            .close()
            .extrude(extrude_w)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box X: from -bx+x_shift to +bx+x_shift
        expected_xmin = -bx + x_shift
        expected_xmax =  bx + x_shift
        expected_xlen = base_len
        assert abs(bb.xmin - expected_xmin) < TOL, f"xmin: expected {expected_xmin:.6f}, got {bb.xmin:.6f}"
        assert abs(bb.xmax - expected_xmax) < TOL, f"xmax: expected {expected_xmax:.6f}, got {bb.xmax:.6f}"
        assert abs(bb.xlen - expected_xlen) < TOL, f"xlen: expected {expected_xlen:.6f}, got {bb.xlen:.6f}"
    
        # Bounding box Z: from 0 to trap_h
        assert abs(bb.zmin - 0.0) < TOL, f"zmin: expected 0.0, got {bb.zmin:.6f}"
        assert abs(bb.zmax - trap_h) < TOL, f"zmax: expected {trap_h:.6f}, got {bb.zmax:.6f}"
        assert abs(bb.zlen - trap_h) < TOL, f"zlen: expected {trap_h:.6f}, got {bb.zlen:.6f}"
    
        # Bounding box Y: extrusion width
        # XZ plane extrudes along -Y by default in CadQuery, check ylen
        assert abs(bb.ylen - extrude_w) < TOL, f"ylen: expected {extrude_w:.6f}, got {bb.ylen:.6f}"
    
        # Volume: trapezoid area * extrude_w
        trap_area = 0.5 * (base_len + top_len) * trap_h
        expected_vol = trap_area * extrude_w
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: trapezoidal prism has 6 faces
        # (2 trapezoidal end faces + 4 rectangular side faces)
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # All faces should be planar
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, f"Planar face count: expected 6, got {planar_count}"
    
        # Edge count: trapezoidal prism has 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # Vertex count: 8
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # Center of mass should be near x_shift in X, trap_h/2 in Z
        com = cq.Shape.centerOfMass(result.val())
        # X center of mass for isosceles trapezoid: x_shift (by symmetry)
        # Actually for isosceles trapezoid, centroid_x = x_shift
        # centroid_z = h/3 * (2*top + base) / (top + base)
        centroid_z = (trap_h / 3.0) * (2.0 * top_len + base_len) / (top_len + base_len)
        assert abs(com.x - x_shift) < TOL, f"COM x: expected {x_shift:.6f}, got {com.x:.6f}"
        assert abs(com.z - centroid_z) < TOL, f"COM z: expected {centroid_z:.6f}, got {com.z:.6f}"
    
        print("All assertions passed!")
        print(f"  Bounding box: x=[{bb.xmin:.5f}, {bb.xmax:.5f}], y=[{bb.ymin:.5f}, {bb.ymax:.5f}], z=[{bb.zmin:.5f}, {bb.zmax:.5f}]")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"  Faces: {face_count}, Edges: {edge_count}, Vertices: {vertex_count}")
        print(f"  COM: ({com.x:.5f}, {com.y:.5f}, {com.z:.5f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00675952/gpt_generated.stl')
