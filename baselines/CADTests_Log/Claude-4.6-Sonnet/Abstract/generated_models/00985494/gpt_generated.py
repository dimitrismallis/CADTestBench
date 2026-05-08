import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        bottom_width = 80.0   # bottom edge length
        top_width    = 40.0   # top edge length
        trap_height  = 40.0   # 2D height of trapezoid
        depth        = 30.0   # extrusion depth (prism thickness)
    
        # Derived: horizontal offset on each side
        offset = (bottom_width - top_width) / 2.0  # = 20.0
    
        # Trapezoid vertices (centered at XY origin):
        #   Bottom-left:  (-bottom_width/2,  -trap_height/2)
        #   Bottom-right: ( bottom_width/2,  -trap_height/2)
        #   Top-right:    ( top_width/2,      trap_height/2)
        #   Top-left:     (-top_width/2,      trap_height/2)
        bx = bottom_width / 2.0   # 40
        tx = top_width    / 2.0   # 20
        by = -trap_height / 2.0   # -20
        ty =  trap_height / 2.0   # +20
    
        # --- Step 1: Draw the regular trapezoid sketch on XY plane ---
        result = (
            cq.Workplane("XY")
            .moveTo(-bx, by)          # bottom-left
            .lineTo( bx, by)          # bottom-right
            .lineTo( tx, ty)          # top-right
            .lineTo(-tx, ty)          # top-left
            .close()                  # back to bottom-left
            # --- Step 2: Extrude to create the prism ---
            .extrude(depth)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - bottom_width) < TOL, \
            f"X extent: expected {bottom_width}, got {bb.xlen}"
        assert abs(bb.ylen - trap_height) < TOL, \
            f"Y extent: expected {trap_height}, got {bb.ylen}"
        assert abs(bb.zlen - depth) < TOL, \
            f"Z extent (depth): expected {depth}, got {bb.zlen}"
    
        # 2. Volume check: trapezoid area = (a + b) / 2 * h
        trap_area = (bottom_width + top_width) / 2.0 * trap_height
        expected_vol = trap_area * depth
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Face count: a prism with trapezoidal cross-section has 6 faces
        #    (2 trapezoidal end faces + 4 rectangular side faces)
        face_count = result.faces().size()
        assert face_count == 6, \
            f"Face count: expected 6, got {face_count}"
    
        # 4. All faces should be planar (no curved surfaces)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, \
            f"Planar face count: expected 6, got {planar_count}"
    
        # 5. Edge count: trapezoid prism has 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, \
            f"Edge count: expected 12, got {edge_count}"
    
        # 6. Vertex count: 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, \
            f"Vertex count: expected 8, got {vertex_count}"
    
        # 7. Center of mass checks
        #    For an isosceles trapezoid with bottom=a, top=b, height=h,
        #    the centroid measured from the bottom edge is:
        #      y_bar = h/3 * (a + 2b) / (a + b)
        #    Since the trapezoid bottom is at y = -trap_height/2, the absolute centroid Y is:
        #      com_y = -trap_height/2 + y_bar
        a = bottom_width
        b = top_width
        h = trap_height
        y_bar = h / 3.0 * (a + 2.0 * b) / (a + b)
        expected_com_y = -trap_height / 2.0 + y_bar
    
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, \
            f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y - expected_com_y) < TOL, \
            f"Center of mass Y: expected {expected_com_y:.6f}, got {com.y:.6f}"
        assert abs(com.z - depth / 2.0) < TOL, \
            f"Center of mass Z: expected {depth/2.0}, got {com.z}"
    
        # 8. Bottom face width check (face at minimum Y)
        bottom_face = result.faces("<Y").val()
        bb_bottom = bottom_face.BoundingBox()
        assert abs(bb_bottom.xlen - bottom_width) < TOL, \
            f"Bottom face width: expected {bottom_width}, got {bb_bottom.xlen}"
    
        # 9. Top face width check (face at maximum Y)
        top_face = result.faces(">Y").val()
        bb_top = top_face.BoundingBox()
        assert abs(bb_top.xlen - top_width) < TOL, \
            f"Top face width: expected {top_width}, got {bb_top.xlen}"
    
        # 10. Confirm the solid is a single solid
        solid_count = result.solids().size()
        assert solid_count == 1, \
            f"Solid count: expected 1, got {solid_count}"
    
        # 11. Leg length check: slanted side = sqrt(offset^2 + trap_height^2)
        leg_length = math.sqrt(offset**2 + trap_height**2)  # sqrt(20^2 + 40^2) ≈ 44.72
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm")
        print(f"  Volume: {actual_vol:.2f} mm³  (expected {expected_vol:.2f})")
        print(f"  Faces: {face_count}, Edges: {edge_count}, Vertices: {vertex_count}")
        print(f"  Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
        print(f"  Expected CoM Y: {expected_com_y:.4f}")
        print(f"  Leg length: {leg_length:.4f} mm")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00985494/gpt_generated.stl')
