import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        base   = 1.04094
        height = 0.465517
        depth  = 0.75
    
        # --- Step 1: Draw right triangle in XY plane ---
        # Right angle at origin, base along X, height along Y
        triangle = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(base, 0)
            .lineTo(0, height)
            .close()
        )
    
        # --- Step 2: Extrude the triangle by depth ---
        result = triangle.extrude(depth)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - base)   < TOL, f"X length: expected {base}, got {bb.xlen}"
        assert abs(bb.ylen - height) < TOL, f"Y length: expected {height}, got {bb.ylen}"
        assert abs(bb.zlen - depth)  < TOL, f"Z length: expected {depth}, got {bb.zlen}"
    
        # Volume check: V = 0.5 * base * height * depth
        expected_vol = 0.5 * base * height * depth
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 1e-4, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: 5 faces (2 triangular end caps + 3 rectangular side faces)
        face_count = result.faces().size()
        assert face_count == 5, f"Face count: expected 5, got {face_count}"
    
        # Edge count: 9 edges (3 per triangle × 2 + 3 longitudinal edges)
        edge_count = result.edges().size()
        assert edge_count == 9, f"Edge count: expected 9, got {edge_count}"
    
        # Vertex count: 6 (3 per triangular face × 2)
        vertex_count = result.vertices().size()
        assert vertex_count == 6, f"Vertex count: expected 6, got {vertex_count}"
    
        # Check that the right-angle corner exists at origin (z=0)
        # The point (0, 0, 0) should be inside or on the boundary of the solid
        solid = result.val()
        assert solid.isInside((0.01, 0.01, 0.01), tolerance=1e-3), \
            "Point near origin should be inside the solid"
    
        # Check that a point outside the triangle is NOT inside the solid
        assert not solid.isInside((base, height, depth / 2), tolerance=1e-3), \
            "Point at (base, height, depth/2) should be outside the solid"
    
        # Planar faces: all 5 faces should be planar (triangular prism has no curved faces)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 5, f"Planar face count: expected 5, got {planar_count}"
    
        # Check bounding box origin alignment
        assert abs(bb.xmin) < TOL, f"X min should be ~0, got {bb.xmin}"
        assert abs(bb.ymin) < TOL, f"Y min should be ~0, got {bb.ymin}"
        assert abs(bb.zmin) < TOL, f"Z min should be ~0, got {bb.zmin}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00006136/gpt_generated.stl')
