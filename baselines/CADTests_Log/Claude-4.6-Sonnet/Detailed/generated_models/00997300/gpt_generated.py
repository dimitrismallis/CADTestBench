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
        cyl_height   = 0.375
        cyl_diameter = 1.5
        cyl_radius   = cyl_diameter / 2.0   # 0.75
    
        central_hole_d = 0.1875
        small_hole_d   = 0.1125
        hole_offset    = 0.24375            # radial distance from center for small holes
    
        # --- Step 1: Create the main cylinder ---
        result = cq.Workplane("XY").cylinder(cyl_height, cyl_radius)
    
        # --- Step 2: Cut the central hole through the cylinder ---
        result = (
            result
            .faces(">Z").workplane()
            .circle(central_hole_d / 2.0)
            .cutThruAll()
        )
    
        # --- Step 3: Cut three smaller holes in triangular formation ---
        # Positions at 0°, 120°, 240° offset by hole_offset from center
        angles_deg = [0, 120, 240]
        small_hole_points = []
        for angle_deg in angles_deg:
            angle_rad = math.radians(angle_deg)
            x = hole_offset * math.cos(angle_rad)
            y = hole_offset * math.sin(angle_rad)
            small_hole_points.append((x, y))
    
        # Use pushPoints to place all three holes at once on a fresh workplane
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints(small_hole_points)
            .circle(small_hole_d / 2.0)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 1e-3
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - cyl_diameter) < TOL, \
            f"X extent: expected {cyl_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - cyl_diameter) < TOL, \
            f"Y extent: expected {cyl_diameter}, got {bb.ylen}"
        assert abs(bb.zlen - cyl_height) < TOL, \
            f"Z extent: expected {cyl_height}, got {bb.zlen}"
    
        # Cylinder is centered at origin: z from -height/2 to +height/2
        assert abs(bb.zmin - (-cyl_height / 2)) < TOL, \
            f"Z min: expected {-cyl_height/2}, got {bb.zmin}"
        assert abs(bb.zmax - (cyl_height / 2)) < TOL, \
            f"Z max: expected {cyl_height/2}, got {bb.zmax}"
    
        # Volume check:
        # Main cylinder volume minus central hole minus 3 small holes
        main_vol    = math.pi * (cyl_radius ** 2) * cyl_height
        central_vol = math.pi * ((central_hole_d / 2) ** 2) * cyl_height
        small_vol   = math.pi * ((small_hole_d / 2) ** 2) * cyl_height
        expected_vol = main_vol - central_vol - 3 * small_vol
    
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face topology checks
        face_count = result.faces().size()
        cyl_face_count = result.faces("%Cylinder").size()
        planar_face_count = result.faces("%Plane").size()
    
        # Planar faces: top + bottom = 2
        assert planar_face_count == 2, \
            f"Planar face count: expected 2, got {planar_face_count}"
    
        # Total faces = cylindrical + planar
        assert face_count == cyl_face_count + planar_face_count, \
            f"Total face count mismatch: {cyl_face_count} cyl + {planar_face_count} planar != {face_count}"
    
        # Check holes exist by probing: points inside holes should be OUTSIDE the solid
        # Central hole: point at (0, 0, 0) should be outside the solid
        assert not solid.isInside((0, 0, 0)), \
            "Central hole: point (0,0,0) should be outside (inside hole)"
    
        # Small holes: points at each hole center at z=0 should be outside
        for angle_deg in angles_deg:
            angle_rad = math.radians(angle_deg)
            x = hole_offset * math.cos(angle_rad)
            y = hole_offset * math.sin(angle_rad)
            assert not solid.isInside((x, y, 0)), \
                f"Small hole at angle {angle_deg}°: point ({x:.4f},{y:.4f},0) should be outside"
    
        # A point well inside the solid body (not in any hole) should be inside
        # Use a point at radius 0.5 (between hole_offset+small_r and outer edge), angle 60°
        test_r = 0.5
        test_x = test_r * math.cos(math.radians(60))
        test_y = test_r * math.sin(math.radians(60))
        assert solid.isInside((test_x, test_y, 0)), \
            f"Solid body: point ({test_x:.4f},{test_y:.4f},0) should be inside"
    
        # Verify center of mass is at origin (symmetric object)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"Center of mass Z: expected 0, got {com.z}"
    
        # Verify holes go all the way through using facesIntersectedByLine
        # A ray along Z through the central hole center should hit 0 solid faces
        central_faces = solid.facesIntersectedByLine((0, 0, -1), (0, 0, 1))
        assert len(central_faces) == 0, \
            f"Central hole: ray through center should hit 0 faces, hit {len(central_faces)}"
    
        # A ray along Z through each small hole center should also hit 0 solid faces
        for angle_deg in angles_deg:
            angle_rad = math.radians(angle_deg)
            x = hole_offset * math.cos(angle_rad)
            y = hole_offset * math.sin(angle_rad)
            small_faces = solid.facesIntersectedByLine((x, y, -1), (0, 0, 1))
            assert len(small_faces) == 0, \
                f"Small hole at {angle_deg}°: ray should hit 0 faces, hit {len(small_faces)}"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.4f} x {bb.ylen:.4f} x {bb.zlen:.4f}")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"  Faces: {face_count} total, {cyl_face_count} cylindrical, {planar_face_count} planar")
        print(f"  Small hole positions: {small_hole_points}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00997300/gpt_generated.stl')
