import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        bottom_base = 60.0   # width of the bottom of the trapezoid
        top_base    = 30.0   # width of the top of the trapezoid
        trap_height = 40.0   # height of the trapezoid cross-section
        extrude_len = 200.0  # length of the prism (large extrusion)
    
        # --- Step 1: Build the isosceles trapezoid profile on the XY plane ---
        # Vertices (centered horizontally):
        #   bottom-left:  (-bottom_base/2, 0)
        #   bottom-right: ( bottom_base/2, 0)
        #   top-right:    ( top_base/2,    trap_height)
        #   top-left:     (-top_base/2,    trap_height)
        half_b = bottom_base / 2.0   # 30
        half_t = top_base    / 2.0   # 15
    
        result = (
            cq.Workplane("XY")
            .moveTo(-half_b, 0)
            .lineTo( half_b, 0)
            .lineTo( half_t, trap_height)
            .lineTo(-half_t, trap_height)
            .close()
            # --- Step 2: Extrude along Z by a large amount ---
            .extrude(extrude_len)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - bottom_base) < TOL, \
            f"X extent (bottom base): expected {bottom_base}, got {bb.xlen}"
        assert abs(bb.ylen - trap_height) < TOL, \
            f"Y extent (trap height): expected {trap_height}, got {bb.ylen}"
        assert abs(bb.zlen - extrude_len) < TOL, \
            f"Z extent (extrude length): expected {extrude_len}, got {bb.zlen}"
    
        # Volume check: area of trapezoid × extrusion length
        # Area of trapezoid = 0.5 * (bottom_base + top_base) * trap_height
        trap_area = 0.5 * (bottom_base + top_base) * trap_height
        expected_vol = trap_area * extrude_len
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count: a trapezoidal prism has 6 faces
        # (2 trapezoidal end caps + 4 rectangular side faces)
        face_count = result.faces().size()
        assert face_count == 6, \
            f"Face count: expected 6, got {face_count}"
    
        # All faces should be planar
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, \
            f"Planar face count: expected 6, got {planar_count}"
    
        # Edge count: trapezoidal prism has 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, \
            f"Edge count: expected 12, got {edge_count}"
    
        # Vertex count: trapezoidal prism has 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, \
            f"Vertex count: expected 8, got {vertex_count}"
    
        # Symmetry: center of mass should be at x=0 (isosceles = symmetric about YZ plane)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, \
            f"Center of mass X (symmetry): expected 0, got {com.x}"
    
        # Center of mass Y should be at centroid of trapezoid
        # Centroid Y of trapezoid = h/3 * (2*top + bottom) / (top + bottom)
        centroid_y = (trap_height / 3.0) * (2.0 * top_base + bottom_base) / (top_base + bottom_base)
        assert abs(com.y - centroid_y) < TOL, \
            f"Center of mass Y: expected {centroid_y:.4f}, got {com.y:.4f}"
    
        # Center of mass Z should be at half the extrusion length
        assert abs(com.z - extrude_len / 2.0) < TOL, \
            f"Center of mass Z: expected {extrude_len/2.0}, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00998283/gpt_generated.stl')
