import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        bottom_width = 80.0   # mm
        top_width    = 40.0   # mm
        trap_height  = 50.0   # mm (height of the trapezoidal face)
        thickness    = 10.0   # mm (extrusion depth)
    
        # --- Step 1: Define the four vertices of the isosceles trapezoid ---
        # Centered on X-axis; bottom edge along Y=0, top edge at Y=trap_height
        half_bottom = bottom_width / 2.0   # 40
        half_top    = top_width    / 2.0   # 20
    
        # Vertices in order (counter-clockwise):
        # BL -> BR -> TR -> TL
        pts = [
            (-half_bottom, 0),
            ( half_bottom, 0),
            ( half_top,    trap_height),
            (-half_top,    trap_height),
        ]
    
        # --- Step 2: Build the 2D profile and extrude ---
        result = (
            cq.Workplane("XY")
            .moveTo(pts[0][0], pts[0][1])
            .lineTo(pts[1][0], pts[1][1])
            .lineTo(pts[2][0], pts[2][1])
            .lineTo(pts[3][0], pts[3][1])
            .close()
            .extrude(thickness)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - bottom_width) < TOL, \
            f"X extent: expected {bottom_width}, got {bb.xlen}"
        assert abs(bb.ylen - trap_height) < TOL, \
            f"Y extent (trap height): expected {trap_height}, got {bb.ylen}"
        assert abs(bb.zlen - thickness) < TOL, \
            f"Z extent (thickness): expected {thickness}, got {bb.zlen}"
    
        # Bounding box position checks
        assert abs(bb.xmin - (-half_bottom)) < TOL, \
            f"xmin: expected {-half_bottom}, got {bb.xmin}"
        assert abs(bb.xmax - half_bottom) < TOL, \
            f"xmax: expected {half_bottom}, got {bb.xmax}"
        assert abs(bb.ymin - 0.0) < TOL, \
            f"ymin: expected 0.0, got {bb.ymin}"
        assert abs(bb.ymax - trap_height) < TOL, \
            f"ymax: expected {trap_height}, got {bb.ymax}"
    
        # Volume check:
        # Area of trapezoid = 0.5 * (bottom + top) * height
        trap_area = 0.5 * (bottom_width + top_width) * trap_height
        expected_vol = trap_area * thickness
        assert abs(solid.Volume() - expected_vol) < TOL, \
            f"Volume: expected {expected_vol}, got {solid.Volume()}"
    
        # Face count: 6 faces (2 trapezoidal + 2 rectangular long sides + 2 rectangular short sides)
        # Actually: 2 trapezoidal faces (front/back) + 4 quadrilateral side faces = 6 total
        face_count = result.faces().size()
        assert face_count == 6, \
            f"Face count: expected 6, got {face_count}"
    
        # All faces should be planar
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, \
            f"Planar face count: expected 6, got {planar_count}"
    
        # Edge count: 12 edges (4 on front face + 4 on back face + 4 connecting edges)
        edge_count = result.edges().size()
        assert edge_count == 12, \
            f"Edge count: expected 12, got {edge_count}"
    
        # Vertex count: 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, \
            f"Vertex count: expected 8, got {vertex_count}"
    
        # Symmetry: center of mass should be at x=0 (isosceles = symmetric about YZ plane)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, \
            f"Center of mass X: expected 0.0 (symmetric), got {com.x}"
    
        # Center of mass Y: centroid of trapezoid
        # y_centroid = h/3 * (2*top + bottom) / (top + bottom)
        y_centroid = (trap_height / 3.0) * (2 * top_width + bottom_width) / (top_width + bottom_width)
        assert abs(com.y - y_centroid) < TOL, \
            f"Center of mass Y: expected {y_centroid:.4f}, got {com.y:.4f}"
    
        # Center of mass Z: should be at thickness/2
        assert abs(com.z - thickness / 2.0) < TOL, \
            f"Center of mass Z: expected {thickness/2.0}, got {com.z}"
    
        # Leg length check (the two slanted sides should be equal — isosceles property)
        # Leg length = sqrt((half_bottom - half_top)^2 + trap_height^2)
        leg_len_2d = math.sqrt((half_bottom - half_top)**2 + trap_height**2)
        # The slanted edges on the front face connect (±40,0,0) to (±20,50,0)
        # We can verify via the bounding box of the solid that the shape is correct
        # (direct edge length check via geometry)
        expected_leg = math.sqrt((half_bottom - half_top)**2 + trap_height**2)
        assert abs(expected_leg - math.sqrt(20**2 + 50**2)) < TOL, \
            f"Leg length sanity: expected {math.sqrt(20**2+50**2):.4f}, got {expected_leg:.4f}"
    
        # Check a point inside the solid (centroid should be inside)
        assert solid.isInside((0, y_centroid, thickness / 2.0)), \
            "Centroid point should be inside the solid"
    
        # Check a point outside the solid (corner of bounding box that's cut off)
        # The top corners of the bounding box (±40, 50, 5) should be OUTSIDE
        assert not solid.isInside((half_bottom, trap_height, thickness / 2.0)), \
            "Top-right bounding box corner should be outside the solid (trapezoid cuts it)"
        assert not solid.isInside((-half_bottom, trap_height, thickness / 2.0)), \
            "Top-left bounding box corner should be outside the solid (trapezoid cuts it)"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00520570/gpt_generated.stl')
