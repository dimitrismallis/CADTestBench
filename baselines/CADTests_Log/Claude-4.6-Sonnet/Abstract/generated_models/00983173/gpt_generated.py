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
        plate_size   = 60.0
        plate_thick  = 4.0
        hole_dia     = 4.0
        hole_offset  = 22.0   # distance from center to hole center along each axis
        cyl_outer_r  = 12.0
        cyl_inner_r  = 8.0
        cyl_height   = 14.0   # taller than plate so it extends through
    
        # --- Step 1: Square plate ---
        plate = cq.Workplane("XY").box(plate_size, plate_size, plate_thick)
    
        # --- Step 2: Four tiny corner holes through the plate ---
        plate = (
            plate
            .faces(">Z").workplane()
            .pushPoints([
                ( hole_offset,  hole_offset),
                (-hole_offset,  hole_offset),
                ( hole_offset, -hole_offset),
                (-hole_offset, -hole_offset),
            ])
            .hole(hole_dia)
        )
    
        # --- Step 3: Solid outer cylinder centered at origin,
        #             extending through the plate (symmetric about XY plane) ---
        outer_cyl = (
            cq.Workplane("XY")
            .circle(cyl_outer_r)
            .extrude(cyl_height / 2, both=True)
        )
    
        # --- Step 4: Union the outer cylinder with the plate ---
        result = plate.union(outer_cyl)
    
        # --- Step 5: Cut the inner bore through the entire unioned solid ---
        # This ensures the bore passes through both the cylinder AND the plate
        result = (
            result
            .faces(">Z").workplane()
            .circle(cyl_inner_r)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box: X and Y should be plate_size (60), Z should be cyl_height (14)
        assert abs(bb.xlen - plate_size) < TOL, \
            f"X extent: expected {plate_size}, got {bb.xlen:.4f}"
        assert abs(bb.ylen - plate_size) < TOL, \
            f"Y extent: expected {plate_size}, got {bb.ylen:.4f}"
        assert abs(bb.zlen - cyl_height) < TOL, \
            f"Z extent: expected {cyl_height}, got {bb.zlen:.4f}"
    
        # Bounding box should be centered at origin
        assert abs(bb.xmin + plate_size / 2) < TOL, \
            f"X min: expected {-plate_size/2}, got {bb.xmin:.4f}"
        assert abs(bb.ymin + plate_size / 2) < TOL, \
            f"Y min: expected {-plate_size/2}, got {bb.ymin:.4f}"
        assert abs(bb.zmin + cyl_height / 2) < TOL, \
            f"Z min: expected {-cyl_height/2}, got {bb.zmin:.4f}"
    
        # Volume check:
        # Union of plate + outer cylinder, then subtract inner bore and corner holes
        #
        # Plate volume
        plate_vol = plate_size * plate_size * plate_thick
        # Outer cylinder volume (full height)
        outer_cyl_vol = math.pi * cyl_outer_r**2 * cyl_height
        # Overlap between plate and outer cylinder (annulus cross-section * plate_thick)
        overlap_vol = math.pi * cyl_outer_r**2 * plate_thick
        # Union volume before any holes = plate + outer_cyl - overlap
        union_vol = plate_vol + outer_cyl_vol - overlap_vol
        # Subtract inner bore (through full height of union = cyl_height)
        inner_bore_vol = math.pi * cyl_inner_r**2 * cyl_height
        # Subtract 4 corner holes (through plate thickness only)
        corner_hole_vol = 4 * math.pi * (hole_dia / 2)**2 * plate_thick
    
        expected_vol = union_vol - inner_bore_vol - corner_hole_vol
    
        actual_vol = result.val().Volume()
        print(f"Expected volume: {expected_vol:.4f}, Actual volume: {actual_vol:.4f}")
        print(f"Relative difference: {abs(actual_vol - expected_vol) / expected_vol:.6f}")
    
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.4f}, got {actual_vol:.4f}, " \
            f"relative diff = {abs(actual_vol - expected_vol)/expected_vol:.6f}"
    
        # Check cylindrical faces exist (outer wall, inner bore, 4 corner holes)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 3, \
            f"Expected at least 3 cylindrical faces (outer wall, inner bore, corner holes), got {cyl_faces}"
    
        # Check the inner bore: center of the solid at Z=0 should be outside (it's the bore)
        solid = result.val()
        bore_test_point = (0.0, 0.0, 0.0)
        assert not solid.isInside(bore_test_point), \
            "Center point should be inside the bore (hollow), but isInside returned True"
    
        # Check a point in the plate material (away from bore and holes) is inside
        plate_material_point = (25.0, 0.0, 0.0)
        assert solid.isInside(plate_material_point), \
            "Point in plate material should be inside the solid"
    
        # Check a point in the cylinder wall above the plate is inside the solid
        cyl_wall_point = (10.0, 0.0, 5.0)
        assert solid.isInside(cyl_wall_point), \
            "Point in cylinder wall above plate should be inside the solid"
    
        # Check a point outside the model is not inside
        outside_point = (35.0, 35.0, 5.0)
        assert not solid.isInside(outside_point), \
            "Point outside the model should not be inside the solid"
    
        # Check that a corner hole location is hollow (outside the solid)
        corner_hole_point = (hole_offset, hole_offset, 0.0)
        assert not solid.isInside(corner_hole_point), \
            f"Corner hole at ({hole_offset},{hole_offset},0) should be hollow"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00983173/gpt_generated.stl')
