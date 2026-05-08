import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        plate_size   = 1.3125   # inches
        plate_h      = 0.0625   # inches
        hole_dia     = 0.05     # inches
        hole_r       = hole_dia / 2.0
        cyl_od       = 1.0      # outer diameter
        cyl_id       = 0.9375   # inner diameter
        cyl_h        = 0.6875   # height
        z_offset     = 0.03125  # translation in Z
    
        # Corner hole inset from edge
        inset = 0.09375  # ~3/32" inset from each edge
        hole_pos = plate_size / 2.0 - inset  # ±0.5625" from center
    
        # --- Step 1: Base plate (centered at origin, XY plane) ---
        plate = (
            cq.Workplane("XY")
            .box(plate_size, plate_size, plate_h)
        )
    
        # --- Step 2: Drill four corner holes through the plate ---
        plate = (
            plate
            .faces(">Z").workplane()
            .pushPoints([
                ( hole_pos,  hole_pos),
                (-hole_pos,  hole_pos),
                (-hole_pos, -hole_pos),
                ( hole_pos, -hole_pos),
            ])
            .hole(hole_dia)
        )
    
        # --- Step 3: Create hollow cylinder (tube) ---
        # Outer cylinder
        outer_cyl = (
            cq.Workplane("XY")
            .cylinder(cyl_h, cyl_od / 2.0)
        )
        # Inner cylinder (bore) — cut through the outer
        inner_cyl = (
            cq.Workplane("XY")
            .cylinder(cyl_h, cyl_id / 2.0)
        )
        hollow_cyl = outer_cyl.cut(inner_cyl)
    
        # --- Step 4: Union plate and hollow cylinder ---
        # The cylinder is centered at (0,0,0) and spans ±cyl_h/2 in Z
        # The plate is centered at (0,0,0) and spans ±plate_h/2 in Z
        # They intersect in the middle — union them
        assembly = plate.union(hollow_cyl)
    
        # --- Step 5: Translate entire assembly by z_offset in Z ---
        assembly = assembly.translate((0, 0, z_offset))
    
        # --- Final object verification ---
        TOL = 0.001
    
        solid = assembly.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks (after Z translation)
        # X and Y: plate dominates at 1.3125"
        assert abs(bb.xlen - plate_size) < TOL, \
            f"X extent: expected {plate_size}, got {bb.xlen}"
        assert abs(bb.ylen - plate_size) < TOL, \
            f"Y extent: expected {plate_size}, got {bb.ylen}"
    
        # Z: cylinder dominates: height = 0.6875, centered at 0 before translation
        # After translation by 0.03125: zmin = -0.34375+0.03125 = -0.3125, zmax = 0.34375+0.03125 = 0.375
        expected_zmin = -cyl_h / 2.0 + z_offset
        expected_zmax =  cyl_h / 2.0 + z_offset
        assert abs(bb.zmin - expected_zmin) < TOL, \
            f"Z min: expected {expected_zmin}, got {bb.zmin}"
        assert abs(bb.zmax - expected_zmax) < TOL, \
            f"Z max: expected {expected_zmax}, got {bb.zmax}"
        assert abs(bb.zlen - cyl_h) < TOL, \
            f"Z extent: expected {cyl_h}, got {bb.zlen}"
    
        # Volume check
        # Plate volume (solid box minus 4 corner holes)
        plate_vol_solid = plate_size * plate_size * plate_h
        hole_vol_each   = math.pi * hole_r**2 * plate_h
        plate_vol       = plate_vol_solid - 4 * hole_vol_each
    
        # Cylinder annulus volume
        cyl_vol = math.pi * ((cyl_od/2)**2 - (cyl_id/2)**2) * cyl_h
    
        # Intersection volume (where cylinder annulus overlaps plate over plate thickness)
        cyl_intersect_vol = math.pi * ((cyl_od/2)**2 - (cyl_id/2)**2) * plate_h
    
        # Union volume = plate_vol + cyl_vol - intersection_vol
        expected_vol = plate_vol + cyl_vol - cyl_intersect_vol
        actual_vol   = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical faces exist (the hollow cylinder walls)
        cyl_faces = assembly.faces("%Cylinder").size()
        assert cyl_faces >= 2, \
            f"Expected at least 2 cylindrical faces (inner+outer), got {cyl_faces}"
    
        # Check symmetry: center of mass should be at X=0, Y=0
        center = cq.Shape.centerOfMass(solid)
        assert abs(center.x) < TOL, f"Center X should be ~0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y should be ~0, got {center.y}"
    
        # After translation: plate spans z=[0.0, 0.0625], plate midpoint z=0.03125
        plate_mid_z = z_offset  # midpoint of plate after translation
    
        # Point in plate corner region (outside cylinder, away from corner holes)
        # hole_pos = 0.5625, hole_r = 0.025 — keep well away from holes
        # Use (0.4, 0.4): distance from center = 0.566 > cyl outer radius 0.5,
        # and far from corner holes at (±0.5625, ±0.5625)
        plate_corner_point = (0.4, 0.4, plate_mid_z)
        # Distance from (0.4,0.4) to cylinder axis = sqrt(0.4^2+0.4^2) ≈ 0.566 > 0.5 (outside cyl)
        # Distance from (0.4,0.4) to nearest hole at (0.5625,0.5625) ≈ 0.230 >> hole_r=0.025
        assert solid.isInside(plate_corner_point), \
            f"Point {plate_corner_point} in plate corner region should be inside the solid"
    
        # Point at bore center above the plate level should be hollow (outside solid)
        # Plate top after translation: z_offset + plate_h/2 = 0.03125 + 0.03125 = 0.0625
        # Pick z well above plate top but inside cylinder: z = 0.15
        bore_z_above_plate = 0.15
        bore_point_above = (0.0, 0.0, bore_z_above_plate)
        assert not solid.isInside(bore_point_above), \
            f"Point {bore_point_above} at bore center above plate should be outside (hollow) the solid"
    
        # Point in cylinder wall above plate level should be inside solid
        wall_r = (cyl_od/2 + cyl_id/2) / 2.0  # midpoint of wall thickness = 0.484375
        wall_point = (wall_r, 0.0, bore_z_above_plate)
        assert solid.isInside(wall_point), \
            f"Point in cylinder wall at r={wall_r:.4f}, z={bore_z_above_plate} should be inside the solid"
    
        # Point at bore center at plate level IS inside solid (plate fills the bore area)
        bore_at_plate = (0.0, 0.0, plate_mid_z)
        assert solid.isInside(bore_at_plate), \
            f"Point at bore center at plate level z={plate_mid_z} should be inside the solid (plate fills it)"
    
        # Verify corner holes exist: points inside hole locations should be outside solid
        # Hole at (hole_pos, hole_pos) = (0.5625, 0.5625), at plate mid Z
        hole_center_point = (hole_pos, hole_pos, plate_mid_z)
        assert not solid.isInside(hole_center_point), \
            f"Point at corner hole center {hole_center_point} should be outside the solid (drilled hole)"
    
        print("All assertions passed!")
        print(f"  Bounding box: X={bb.xlen:.5f}, Y={bb.ylen:.5f}, Z={bb.zlen:.5f}")
        print(f"  Z range: [{bb.zmin:.5f}, {bb.zmax:.5f}]")
        print(f"  Volume: {actual_vol:.6f} (expected ~{expected_vol:.6f})")
        print(f"  Cylindrical faces: {cyl_faces}")
        print(f"  Hole positions: ±{hole_pos:.5f}")
    
        return assembly
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00983173/gpt_generated.stl')
