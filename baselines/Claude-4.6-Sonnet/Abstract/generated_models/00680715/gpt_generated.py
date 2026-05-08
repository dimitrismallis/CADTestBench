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
        outer_radius = 15.0   # outer radius of the ring
        inner_radius = 10.0   # inner radius of the ring (hole)
        extrude_length = 40.0 # length of extrusion along X-axis
    
        # --- Step 1: Create the ring profile on the YZ plane ---
        # The YZ plane faces the X-axis, so extruding in the normal direction
        # goes along the X-axis.
        # Draw outer circle, then subtract inner circle to form an annular ring.
        ring_profile = (
            cq.Workplane("YZ")
            .circle(outer_radius)   # outer boundary
            .circle(inner_radius)   # inner boundary (creates a hole when extruded)
        )
    
        # --- Step 2: Extrude the ring profile along the X-axis ---
        result = ring_profile.extrude(extrude_length)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Check bounding box dimensions
        bb = result.val().BoundingBox()
    
        # X extent should equal extrude_length (40 mm)
        assert abs(bb.xlen - extrude_length) < TOL, \
            f"X length: expected {extrude_length}, got {bb.xlen}"
    
        # Y extent should equal 2 * outer_radius (30 mm)
        expected_yz_span = 2 * outer_radius
        assert abs(bb.ylen - expected_yz_span) < TOL, \
            f"Y length: expected {expected_yz_span}, got {bb.ylen}"
    
        # Z extent should equal 2 * outer_radius (30 mm)
        assert abs(bb.zlen - expected_yz_span) < TOL, \
            f"Z length: expected {expected_yz_span}, got {bb.zlen}"
    
        # Check volume: annular cross-section area * length
        annular_area = math.pi * (outer_radius**2 - inner_radius**2)
        expected_volume = annular_area * extrude_length
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.01, \
            f"Volume: expected ~{expected_volume:.2f}, got {actual_volume:.2f}"
    
        # Check cylindrical faces: should have 2 (outer cylinder + inner cylinder)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, \
            f"Cylindrical faces: expected 2 (inner + outer), got {cyl_faces}"
    
        # Check planar faces: should have 2 (the two annular end caps)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 2, \
            f"Planar faces: expected 2 (two annular end caps), got {planar_faces}"
    
        # Check total face count: 2 cylindrical + 2 planar = 4
        total_faces = result.faces().size()
        assert total_faces == 4, \
            f"Total faces: expected 4, got {total_faces}"
    
        # Check that the center of mass is at the geometric center
        com = cq.Shape.centerOfMass(result.val())
        # Center should be at (extrude_length/2, 0, 0) since YZ plane is at x=0
        assert abs(com.x - extrude_length / 2) < TOL, \
            f"Center of mass X: expected {extrude_length/2}, got {com.x}"
        assert abs(com.y) < TOL, \
            f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, \
            f"Center of mass Z: expected 0, got {com.z}"
    
        # Check that a point inside the tube wall is inside the solid
        mid_x = extrude_length / 2
        mid_r = (outer_radius + inner_radius) / 2  # midpoint of wall
        assert result.val().isInside((mid_x, mid_r, 0)), \
            "Point in tube wall should be inside the solid"
    
        # Check that a point in the hollow center is NOT inside the solid
        assert not result.val().isInside((mid_x, 0, 0)), \
            "Point in hollow center should NOT be inside the solid"
    
        print("All assertions passed!")
        print(f"  Bounding box: X={bb.xlen:.2f}, Y={bb.ylen:.2f}, Z={bb.zlen:.2f}")
        print(f"  Volume: {actual_volume:.2f} mm³ (expected {expected_volume:.2f})")
        print(f"  Cylindrical faces: {cyl_faces}, Planar faces: {planar_faces}")
        print(f"  Center of mass: ({com.x:.3f}, {com.y:.3f}, {com.z:.3f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00680715/gpt_generated.stl')
