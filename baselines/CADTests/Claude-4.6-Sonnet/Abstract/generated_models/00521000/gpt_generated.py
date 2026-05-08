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
        outer_radius = 15.0      # outer radius of ring
        inner_radius = 12.0      # inner radius of ring
        ring_width = outer_radius - inner_radius  # = 3.0 mm
        ring_height = 2.0        # thickness of ring (height)
    
        hole_diameter = 1.5      # hole diameter < ring_width (3mm)
        hole_radius = hole_diameter / 2.0
        hole_circle_radius = (outer_radius + inner_radius) / 2.0  # = 13.5 mm (centerline of ring)
    
        # --- Step 1: Create the flat ring (annulus) ---
        # Build as outer cylinder minus inner cylinder
        ring = (
            cq.Workplane("XY")
            .circle(outer_radius)
            .extrude(ring_height)
            .faces(">Z")
            .workplane()
            .circle(inner_radius)
            .cutThruAll()
        )
    
        # --- Step 2: Create three holes in triangular formation ---
        # Place holes at 120° intervals on the ring centerline
        # Angles: 90°, 210°, 330° (pointing up, lower-left, lower-right)
        angles_deg = [90, 210, 330]
        hole_positions = [
            (hole_circle_radius * math.cos(math.radians(a)),
             hole_circle_radius * math.sin(math.radians(a)))
            for a in angles_deg
        ]
    
        result = ring
        for (hx, hy) in hole_positions:
            result = (
                result
                .faces(">Z")
                .workplane()
                .pushPoints([(hx, hy)])
                .circle(hole_radius)
                .cutThruAll()
            )
    
        # --- Final object verification ---
        TOL = 0.05
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 2 * outer_radius) < TOL, \
            f"X extent: expected {2*outer_radius}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * outer_radius) < TOL, \
            f"Y extent: expected {2*outer_radius}, got {bb.ylen}"
        assert abs(bb.zlen - ring_height) < TOL, \
            f"Z extent: expected {ring_height}, got {bb.zlen}"
    
        # Volume check
        # Ring volume = pi*(R_outer^2 - R_inner^2)*h - 3 * pi*r_hole^2 * h
        ring_vol = math.pi * (outer_radius**2 - inner_radius**2) * ring_height
        holes_vol = 3 * math.pi * hole_radius**2 * ring_height
        expected_vol = ring_vol - holes_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.3f}, got {actual_vol:.3f}"
    
        # Cylindrical faces: 
        # - 1 outer cylinder face
        # - 1 inner cylinder face (bore)
        # - 3 small hole cylinder faces
        # Total = 5 cylindrical faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 5, \
            f"Cylindrical faces: expected 5 (outer + inner bore + 3 holes), got {cyl_faces}"
    
        # Planar faces: top and bottom = 2 planar annular faces
        # (each has the ring annulus minus 3 holes, but they are still single planar faces)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 2, \
            f"Planar faces: expected 2 (top + bottom), got {planar_faces}"
    
        # Check holes are actually through the ring (points inside holes should be outside solid)
        solid = result.val()
        # A point at the center of one hole should be outside the solid
        hx0, hy0 = hole_positions[0]
        hole_center_point = (hx0, hy0, ring_height / 2.0)
        assert not solid.isInside(hole_center_point, tolerance=0.01), \
            f"Point at hole center {hole_center_point} should be outside solid (hole should exist)"
    
        # A point on the ring body (not in a hole) should be inside the solid
        body_point = (hole_circle_radius, 0, ring_height / 2.0)  # at 0° on centerline
        assert solid.isInside(body_point, tolerance=0.01), \
            f"Point on ring body {body_point} should be inside solid"
    
        # Check center of mass is near origin (symmetric ring)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"Center of mass X: expected ~0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected ~0, got {com.y}"
        assert abs(com.z - ring_height / 2.0) < TOL, \
            f"Center of mass Z: expected ~{ring_height/2.0}, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00521000/gpt_generated.stl')
