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
        base   = 0.95149   # base length of isosceles triangle
        height = 0.15482   # height of isosceles triangle
        depth  = 0.11183   # extrusion depth
    
        half_base = base / 2.0
    
        # --- Step 1: Draw the isosceles triangle profile on XY plane ---
        # Vertices:
        #   Left base corner:  (-half_base, 0)
        #   Right base corner: ( half_base, 0)
        #   Apex:              (0, height)
        # We draw the closed wire using lineTo / close()
        triangle = (
            cq.Workplane("XY")
            .moveTo(-half_base, 0)
            .lineTo( half_base, 0)
            .lineTo(0, height)
            .close()
        )
    
        # --- Step 2: Extrude the triangle profile by depth ---
        result = triangle.extrude(depth)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - base)   < TOL, f"X length: expected {base}, got {bb.xlen}"
        assert abs(bb.ylen - height) < TOL, f"Y length: expected {height}, got {bb.ylen}"
        assert abs(bb.zlen - depth)  < TOL, f"Z length: expected {depth}, got {bb.zlen}"
    
        # Bounding box extents
        assert abs(bb.xmin - (-half_base)) < TOL, f"xmin: expected {-half_base}, got {bb.xmin}"
        assert abs(bb.xmax -   half_base)  < TOL, f"xmax: expected {half_base}, got {bb.xmax}"
        assert abs(bb.ymin - 0.0)          < TOL, f"ymin: expected 0.0, got {bb.ymin}"
        assert abs(bb.ymax - height)       < TOL, f"ymax: expected {height}, got {bb.ymax}"
        assert abs(bb.zmin - 0.0)          < TOL, f"zmin: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - depth)        < TOL, f"zmax: expected {depth}, got {bb.zmax}"
    
        # Volume: area of triangle * depth = (0.5 * base * height) * depth
        expected_vol = 0.5 * base * height * depth
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: a triangular prism has 5 faces
        # (2 triangular end caps + 3 rectangular side faces)
        face_count = result.faces().size()
        assert face_count == 5, f"Face count: expected 5, got {face_count}"
    
        # Edge count: a triangular prism has 9 edges
        edge_count = result.edges().size()
        assert edge_count == 9, f"Edge count: expected 9, got {edge_count}"
    
        # Vertex count: a triangular prism has 6 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 6, f"Vertex count: expected 6, got {vertex_count}"
    
        # Check that all faces are planar (no curved faces)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 5, f"Planar face count: expected 5, got {planar_count}"
    
        # Check the two triangular faces (top and bottom) exist
        bottom_face = result.faces("<Z").size()
        top_face    = result.faces(">Z").size()
        assert bottom_face == 1, f"Bottom face count: expected 1, got {bottom_face}"
        assert top_face    == 1, f"Top face count: expected 1, got {top_face}"
    
        # Center of mass should be at (0, height/3, depth/2) for this isosceles triangle prism
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x - 0.0)          < TOL, f"CoM X: expected 0.0, got {com.x}"
        assert abs(com.y - height / 3.0) < TOL, f"CoM Y: expected {height/3.0}, got {com.y}"
        assert abs(com.z - depth / 2.0)  < TOL, f"CoM Z: expected {depth/2.0}, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00520453/gpt_generated.stl')
