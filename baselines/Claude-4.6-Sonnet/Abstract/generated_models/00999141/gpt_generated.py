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
        bottom_width = 80.0       # bottom base length (mm)
        base_angle_deg = 70.0     # base angle in degrees
        height = 40.0             # trapezoid height (mm)
        extrude_depth = 5.0       # extrusion thickness (mm)
    
        # --- Step 1: Compute trapezoid geometry ---
        # For an isosceles trapezoid with base angle θ:
        # horizontal offset = height / tan(θ)
        base_angle_rad = math.radians(base_angle_deg)
        offset = height / math.tan(base_angle_rad)  # ≈ 14.56 mm
        top_width = bottom_width - 2 * offset        # ≈ 50.88 mm
    
        # Vertices (centered at origin in XY plane by bounding box):
        half_bottom = bottom_width / 2.0
        half_top    = top_width / 2.0
        half_height = height / 2.0
    
        # Vertices in CCW order:
        bl = (-half_bottom, -half_height)  # bottom-left
        br = ( half_bottom, -half_height)  # bottom-right
        tr = ( half_top,     half_height)  # top-right
        tl = (-half_top,     half_height)  # top-left
    
        # --- Step 2: Draw the trapezoid sketch and extrude ---
        result = (
            cq.Workplane("XY")
            .moveTo(*bl)
            .lineTo(*br)
            .lineTo(*tr)
            .lineTo(*tl)
            .close()
            .extrude(extrude_depth)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - bottom_width) < TOL, \
            f"X extent: expected {bottom_width}, got {bb.xlen}"
        assert abs(bb.ylen - height) < TOL, \
            f"Y extent: expected {height}, got {bb.ylen}"
        assert abs(bb.zlen - extrude_depth) < TOL, \
            f"Z extent (extrusion): expected {extrude_depth}, got {bb.zlen}"
    
        # Volume check: trapezoid area = 0.5 * (bottom + top) * height
        trap_area = 0.5 * (bottom_width + top_width) * height
        expected_vol = trap_area * extrude_depth
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count: a prism from a quadrilateral has 6 faces
        # (2 trapezoid faces + 4 side faces)
        face_count = result.faces().size()
        assert face_count == 6, \
            f"Face count: expected 6, got {face_count}"
    
        # All faces should be planar (no cylinders)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, \
            f"Planar face count: expected 6, got {planar_count}"
    
        # Top and bottom faces (parallel to XY plane)
        horiz_faces = result.faces("|Z").size()
        assert horiz_faces == 2, \
            f"Horizontal faces (|Z): expected 2, got {horiz_faces}"
    
        # Check the top and bottom face areas equal the trapezoid area
        top_face_area    = result.faces(">Z").val().Area()
        bottom_face_area = result.faces("<Z").val().Area()
        assert abs(top_face_area - trap_area) / trap_area < 0.01, \
            f"Top face area: expected {trap_area:.2f}, got {top_face_area:.2f}"
        assert abs(bottom_face_area - trap_area) / trap_area < 0.01, \
            f"Bottom face area: expected {trap_area:.2f}, got {bottom_face_area:.2f}"
    
        # Symmetry: center of mass X should be 0 (isosceles = left-right symmetric)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, \
            f"Center of mass X: expected ~0, got {com.x}"
    
        # Center of mass Z should be at half the extrusion depth
        assert abs(com.z - extrude_depth / 2.0) < TOL, \
            f"Center of mass Z: expected {extrude_depth/2.0}, got {com.z}"
    
        # Center of mass Y for a trapezoid (measured from bottom edge):
        # ȳ_from_bottom = h/3 * (2*top + bottom) / (top + bottom)
        # Since bottom edge is at y = -half_height, centroid Y in world coords:
        y_from_bottom = (height / 3.0) * (2.0 * top_width + bottom_width) / (top_width + bottom_width)
        expected_com_y = -half_height + y_from_bottom
        assert abs(com.y - expected_com_y) < TOL, \
            f"Center of mass Y: expected {expected_com_y:.4f}, got {com.y:.4f}"
    
        # Verify the base angle is approximately 70 degrees
        computed_angle = math.degrees(math.atan(height / offset))
        assert abs(computed_angle - base_angle_deg) < 0.5, \
            f"Base angle: expected {base_angle_deg}°, got {computed_angle:.2f}°"
    
        # Edge count: trapezoid prism has 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, \
            f"Edge count: expected 12, got {edge_count}"
    
        # Vertex count: trapezoid prism has 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, \
            f"Vertex count: expected 8, got {vertex_count}"
    
        print(f"Trapezoid plate created successfully!")
        print(f"  Bottom width: {bottom_width} mm, Top width: {top_width:.2f} mm")
        print(f"  Height: {height} mm, Base angle: {base_angle_deg}°")
        print(f"  Extrusion depth: {extrude_depth} mm")
        print(f"  Volume: {actual_vol:.2f} mm³")
        print(f"  Offset per side: {offset:.2f} mm")
        print(f"  Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00999141/gpt_generated.stl')
