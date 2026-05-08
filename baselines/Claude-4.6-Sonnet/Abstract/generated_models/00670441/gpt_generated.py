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
        diameter = 20.0   # circumscribed circle diameter (vertex-to-vertex)
        height   = 10.0   # extrusion height
    
        # --- Step 1: Create a regular octagon on the XY plane ---
        # polygon(nSides, diameter) creates a regular polygon inscribed in a circle
        # of the given diameter (vertex-to-vertex)
        octagon_profile = cq.Workplane("XY").polygon(8, diameter)
    
        # --- Step 2: Extrude the octagon upward along +Z ---
        result = octagon_profile.extrude(height)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 2a. Bounding box checks
        bb = result.val().BoundingBox()
    
        # The circumscribed radius R = diameter / 2 = 10
        R = diameter / 2.0
        # For a regular octagon, the inradius (center to flat side) = R * cos(π/8)
        inradius = R * math.cos(math.pi / 8)
        # The bounding box in X and Y equals the flat-to-flat distance = 2 * inradius
        flat_to_flat = 2.0 * inradius
    
        # X and Y extents: the octagon fits in a square of side = flat_to_flat
        # (since the octagon is axis-aligned, the widest points are the flat sides)
        # Actually for a regular octagon inscribed in circle of radius R,
        # the bounding box is 2*R in both X and Y (vertex-to-vertex along axes)
        # Let's compute correctly:
        # Vertices at angles k*45° for k=0..7
        # x-coords: R*cos(k*45°), y-coords: R*sin(k*45°)
        # max x = R*cos(0°) = R, max y = R*cos(0°) = R  → bbox = 2R x 2R
        # But wait: cos(22.5°) > cos(0°)? No. cos(0°)=1 is max.
        # Actually vertices at 22.5°, 67.5°, 112.5°, ... (offset by 22.5° for flat-top)
        # CadQuery polygon starts at angle 0 by default.
        # Let's just check the bbox is within [flat_to_flat, diameter] range
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
        assert bb.xlen <= diameter + TOL, f"X extent should be <= diameter={diameter}, got {bb.xlen}"
        assert bb.ylen <= diameter + TOL, f"Y extent should be <= diameter={diameter}, got {bb.ylen}"
        assert bb.xlen >= flat_to_flat - TOL, f"X extent should be >= flat_to_flat={flat_to_flat:.4f}, got {bb.xlen}"
        assert bb.ylen >= flat_to_flat - TOL, f"Y extent should be >= flat_to_flat={flat_to_flat:.4f}, got {bb.ylen}"
    
        # 2b. Volume check
        # Area of regular octagon = 2*(1+sqrt(2))*s^2
        # where s = side length = 2*R*sin(π/8)
        s = 2.0 * R * math.sin(math.pi / 8)
        octagon_area = 2.0 * (1.0 + math.sqrt(2.0)) * s**2
        expected_volume = octagon_area * height
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.001, \
            f"Volume: expected ~{expected_volume:.4f}, got {actual_volume:.4f}"
    
        # 2c. Face count: 1 top + 1 bottom + 8 side faces = 10 total
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # 2d. All faces should be planar (no curved faces)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 10, f"Planar face count: expected 10, got {planar_face_count}"
    
        # 2e. Edge count: 8 top edges + 8 bottom edges + 8 vertical edges = 24 total
        edge_count = result.edges().size()
        assert edge_count == 24, f"Edge count: expected 24, got {edge_count}"
    
        # 2f. Vertex count: 8 top + 8 bottom = 16 total
        vertex_count = result.vertices().size()
        assert vertex_count == 16, f"Vertex count: expected 16, got {vertex_count}"
    
        # 2g. Top and bottom faces exist at correct Z positions
        top_z = result.faces(">Z").val().Center().z
        bot_z = result.faces("<Z").val().Center().z
        assert abs(top_z - height) < TOL, f"Top face Z center: expected {height}, got {top_z}"
        assert abs(bot_z - 0.0) < TOL, f"Bottom face Z center: expected 0.0, got {bot_z}"
    
        # 2h. Symmetry: center of mass should be at (0, 0, height/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - height / 2.0) < TOL, f"CoM Z: expected {height/2.0}, got {com.z}"
    
        # 2i. Vertical edges (parallel to Z): should be 8
        vertical_edge_count = result.edges("|Z").size()
        assert vertical_edge_count == 8, f"Vertical edges: expected 8, got {vertical_edge_count}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00670441/gpt_generated.stl')
