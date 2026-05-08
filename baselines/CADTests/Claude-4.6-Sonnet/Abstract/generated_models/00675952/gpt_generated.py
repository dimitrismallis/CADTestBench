import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        bottom_base = 60.0   # length of bottom edge
        top_base    = 30.0   # length of top edge
        trap_height = 40.0   # height of the trapezoid (in Y)
        extrude_depth = 20.0 # depth of extrusion (in Z)
    
        # Trapezoid vertices (centered horizontally about X=0):
        #   Bottom-left:  (-30, -20)
        #   Bottom-right: ( 30, -20)
        #   Top-right:    ( 15,  20)
        #   Top-left:     (-15,  20)
        half_bottom = bottom_base / 2.0   # 30
        half_top    = top_base    / 2.0   # 15
        half_height = trap_height / 2.0   # 20
    
        # --- Step 1: Draw the trapezoid profile on the XY plane ---
        result = (
            cq.Workplane("XY")
            .moveTo(-half_bottom, -half_height)          # bottom-left
            .lineTo( half_bottom, -half_height)          # bottom-right
            .lineTo( half_top,     half_height)          # top-right
            .lineTo(-half_top,     half_height)          # top-left
            .close()                                     # back to bottom-left
        )
    
        # --- Step 2: Extrude the trapezoid sketch to form the prism ---
        result = result.extrude(extrude_depth)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 2a. Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - bottom_base)   < TOL, f"X extent: expected {bottom_base}, got {bb.xlen}"
        assert abs(bb.ylen - trap_height)   < TOL, f"Y extent: expected {trap_height}, got {bb.ylen}"
        assert abs(bb.zlen - extrude_depth) < TOL, f"Z extent: expected {extrude_depth}, got {bb.zlen}"
    
        # 2b. Bounding box position (centered in X and Y, Z from 0 to extrude_depth)
        assert abs(bb.xmin - (-half_bottom)) < TOL, f"xmin: expected {-half_bottom}, got {bb.xmin}"
        assert abs(bb.xmax -   half_bottom)  < TOL, f"xmax: expected {half_bottom}, got {bb.xmax}"
        assert abs(bb.ymin - (-half_height)) < TOL, f"ymin: expected {-half_height}, got {bb.ymin}"
        assert abs(bb.ymax -   half_height)  < TOL, f"ymax: expected {half_height}, got {bb.ymax}"
        assert abs(bb.zmin - 0.0)            < TOL, f"zmin: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - extrude_depth)  < TOL, f"zmax: expected {extrude_depth}, got {bb.zmax}"
    
        # 2c. Volume check
        # Trapezoid area = 0.5 * (bottom_base + top_base) * trap_height
        trap_area     = 0.5 * (bottom_base + top_base) * trap_height
        expected_vol  = trap_area * extrude_depth
        actual_vol    = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 2d. Face count: a trapezoidal prism has 6 faces
        #     (2 trapezoidal end faces + 4 rectangular side faces)
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # 2e. All faces should be planar (no curved surfaces)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 6, f"Planar face count: expected 6, got {planar_face_count}"
    
        # 2f. Edge count: a trapezoidal prism has 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # 2g. Vertex count: a trapezoidal prism has 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # 2h. Two faces parallel to XY plane (top and bottom trapezoidal faces)
        z_parallel_faces = result.faces("|Z").size()
        assert z_parallel_faces == 2, f"Faces parallel to Z: expected 2, got {z_parallel_faces}"
    
        # 2i. The bottom face (min Z) should be at z = 0
        bottom_face_z = result.faces("<Z").val().Center().z
        assert abs(bottom_face_z - 0.0) < TOL, f"Bottom face Z center: expected 0.0, got {bottom_face_z}"
    
        # 2j. The top face (max Z) should be at z = extrude_depth
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - extrude_depth) < TOL, f"Top face Z center: expected {extrude_depth}, got {top_face_z}"
    
        # 2k. Center of mass checks
        # Centroid of trapezoid measured from the bottom edge (y = -half_height):
        # y_c_from_bottom = h/3 * (2*top_base + bottom_base) / (top_base + bottom_base)
        # Then shift by the bottom edge position: centroid_y = -half_height + y_c_from_bottom
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0.0, got {com.x}"
    
        y_c_from_bottom = (trap_height / 3.0) * (2.0 * top_base + bottom_base) / (top_base + bottom_base)
        centroid_y = -half_height + y_c_from_bottom
        assert abs(com.y - centroid_y) < TOL, \
            f"Center of mass Y: expected {centroid_y:.4f}, got {com.y:.4f}"
        assert abs(com.z - extrude_depth / 2.0) < TOL, \
            f"Center of mass Z: expected {extrude_depth/2:.2f}, got {com.z:.4f}"
    
        print(f"All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm")
        print(f"  Volume: {actual_vol:.2f} mm³ (expected {expected_vol:.2f} mm³)")
        print(f"  Faces: {face_count}, Edges: {edge_count}, Vertices: {vertex_count}")
        print(f"  Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00675952/gpt_generated.stl')
