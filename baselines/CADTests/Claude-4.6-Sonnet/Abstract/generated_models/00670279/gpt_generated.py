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
        outer_radius = 15.0   # mm
        inner_radius = 10.0   # mm
        extrude_length = 40.0 # mm along Y-axis
    
        # --- Step 1: Create the ring (annulus) profile on the XZ plane ---
        # The XZ plane has its normal along -Y, so extruding will go in -Y direction.
        ring_profile = cq.Workplane("XZ")
    
        # --- Step 2: Draw the outer circle ---
        ring_profile = ring_profile.circle(outer_radius)
    
        # --- Step 3: Draw the inner circle (creates a hole / annulus) ---
        ring_profile = ring_profile.circle(inner_radius)
    
        # --- Step 4: Extrude along the Y-axis ---
        # Extruding from XZ plane goes in the -Y direction
        result = ring_profile.extrude(extrude_length)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Check bounding box
        bb = result.val().BoundingBox()
    
        # X extent: should span from -outer_radius to +outer_radius
        assert abs(bb.xlen - 2 * outer_radius) < TOL, \
            f"X length: expected {2*outer_radius}, got {bb.xlen}"
    
        # Z extent: should span from -outer_radius to +outer_radius
        assert abs(bb.zlen - 2 * outer_radius) < TOL, \
            f"Z length: expected {2*outer_radius}, got {bb.zlen}"
    
        # Y extent: should equal extrude_length
        assert abs(bb.ylen - extrude_length) < TOL, \
            f"Y length (extrusion): expected {extrude_length}, got {bb.ylen}"
    
        # Volume check: annulus area * length
        annulus_area = math.pi * (outer_radius**2 - inner_radius**2)
        expected_volume = annulus_area * extrude_length
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.001, \
            f"Volume: expected ~{expected_volume:.2f}, got {actual_volume:.2f}"
    
        # Check cylindrical faces: should have 2 (outer and inner curved surfaces)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, \
            f"Cylindrical faces: expected 2 (inner + outer), got {cyl_faces}"
    
        # Check planar faces: should have 2 (top and bottom annular faces)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 2, \
            f"Planar faces: expected 2 (two annular ends), got {planar_faces}"
    
        # Check total face count: 2 cylindrical + 2 planar = 4
        total_faces = result.faces().size()
        assert total_faces == 4, \
            f"Total faces: expected 4, got {total_faces}"
    
        # Check circular edges: should have 4 (2 circles on each end cap)
        circular_edges = result.edges("%Circle").size()
        assert circular_edges == 4, \
            f"Circular edges: expected 4, got {circular_edges}"
    
        # Check that the center of the solid is at the origin in X and Z,
        # and at -extrude_length/2 in Y (extrusion goes in -Y from XZ plane)
        center = result.val().Center()
        assert abs(center.x) < TOL, \
            f"Center X: expected 0, got {center.x}"
        assert abs(center.z) < TOL, \
            f"Center Z: expected 0, got {center.z}"
        assert abs(center.y - (-extrude_length / 2)) < TOL, \
            f"Center Y: expected {-extrude_length/2}, got {center.y}"
    
        # Check that a point inside the tube wall is inside the solid
        mid_wall_radius = (outer_radius + inner_radius) / 2  # 12.5 mm
        assert result.val().isInside((mid_wall_radius, -extrude_length / 2, 0)), \
            "Point in tube wall should be inside the solid"
    
        # Check that a point in the hollow center is NOT inside the solid
        assert not result.val().isInside((0, -extrude_length / 2, 0)), \
            "Point in hollow center should NOT be inside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00670279/gpt_generated.stl')
