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
        R = 15.0        # outer circle radius
        r = 8.0         # inner (cutout) circle radius
        offset = 10.0   # center offset along X for each circle pair
        thickness = 5.0 # extrusion height
    
        # Center positions
        c1 = (-offset, 0)  # left circle center
        c2 = ( offset, 0)  # right circle center
    
        # --- Step 1: Build the outer profile using Sketch API ---
        # Union of two overlapping circles (same radius R)
        outer_sketch = (
            cq.Sketch()
            .push([c1]).circle(R, mode="a")
            .reset()
            .push([c2]).circle(R, mode="a")
            .reset()
        )
    
        # --- Step 2: Subtract two smaller overlapping circles (cutout holes) ---
        # Same centers, smaller radius r
        full_sketch = (
            cq.Sketch()
            .push([c1]).circle(R, mode="a")
            .reset()
            .push([c2]).circle(R, mode="a")
            .reset()
            .push([c1]).circle(r, mode="s")
            .reset()
            .push([c2]).circle(r, mode="s")
            .reset()
        )
    
        # --- Step 3: Extrude the sketch to create the 3D solid ---
        result = cq.Workplane("XY").placeSketch(full_sketch).extrude(thickness)
    
        # --- Final object verification ---
        TOL = 0.5  # tolerance for geometric checks
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks:
        # X extent: from -(offset + R) to +(offset + R) = -25 to 25 → xlen = 50
        expected_xlen = 2 * (offset + R)  # = 50
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen}, got {bb.xlen}"
    
        # Y extent: from -R to +R = -15 to 15 → ylen = 30
        expected_ylen = 2 * R  # = 30
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen}, got {bb.ylen}"
    
        # Z extent: thickness
        assert abs(bb.zlen - thickness) < TOL, \
            f"Z length: expected {thickness}, got {bb.zlen}"
    
        # Volume check:
        # Area of union of two circles = 2*pi*R^2 - intersection_area
        # Intersection area of two circles with radius R and center distance d=2*offset:
        d = 2 * offset  # = 20
        # Each circle segment: half-angle alpha = arccos(d/(2R))
        alpha = math.acos(d / (2 * R))  # arccos(20/30) = arccos(2/3)
        # Intersection area = 2 * R^2 * (alpha - sin(alpha)*cos(alpha))
        intersection_outer = 2 * R**2 * (alpha - math.sin(alpha) * math.cos(alpha))
        area_outer = 2 * math.pi * R**2 - intersection_outer
    
        # Same for inner circles with radius r
        # Check if circles overlap: d < 2*r → 20 < 16? No, d=20 > 2*r=16
        # So inner circles do NOT overlap — they are separate
        # Each inner circle is fully within the outer union (check: center at ±10, radius 8 → max reach ±18 < ±25)
        area_inner = 2 * math.pi * r**2  # two separate circles, no overlap
    
        expected_area = area_outer - area_inner
        expected_volume = expected_area * thickness
    
        actual_volume = solid.Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.02, \
            f"Volume: expected ~{expected_volume:.2f}, got {actual_volume:.2f}"
    
        # Check cylindrical faces exist (from the circular boundaries)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 4, \
            f"Expected at least 4 cylindrical faces (outer + inner arcs), got {cyl_faces}"
    
        # Check top and bottom planar faces exist
        top_faces = result.faces(">Z").size()
        assert top_faces >= 1, f"Expected at least 1 top face, got {top_faces}"
        bot_faces = result.faces("<Z").size()
        assert bot_faces >= 1, f"Expected at least 1 bottom face, got {bot_faces}"
    
        # Check the object is centered near X=0 (symmetric)
        center = solid.Center()
        assert abs(center.x) < TOL, \
            f"Center X should be ~0 (symmetric), got {center.x}"
        assert abs(center.y) < TOL, \
            f"Center Y should be ~0 (symmetric), got {center.y}"
        assert abs(center.z - thickness / 2) < TOL, \
            f"Center Z should be ~{thickness/2}, got {center.z}"
    
        # Check holes exist: a point inside an inner circle should be outside the solid
        # Point at left circle center (c1 = (-10, 0)) at mid-height — inside the hole
        hole_point_left = cq.Vector(c1[0], c1[1], thickness / 2)
        assert not solid.isInside(hole_point_left), \
            f"Point at left hole center should be outside solid (inside hole)"
    
        hole_point_right = cq.Vector(c2[0], c2[1], thickness / 2)
        assert not solid.isInside(hole_point_right), \
            f"Point at right hole center should be outside solid (inside hole)"
    
        # Check that a point in the outer ring (between inner and outer radius) IS inside the solid
        # At left circle: point at radius (R+r)/2 from c1 along +Y
        mid_r = (R + r) / 2  # = 11.5
        ring_point = cq.Vector(c1[0], mid_r, thickness / 2)
        assert solid.isInside(ring_point), \
            f"Point in outer ring at {ring_point} should be inside solid"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"  Volume: {actual_volume:.2f} (expected {expected_volume:.2f})")
        print(f"  Cylindrical faces: {cyl_faces}")
        print(f"  Center: ({center.x:.3f}, {center.y:.3f}, {center.z:.3f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00996457/gpt_generated.stl')
