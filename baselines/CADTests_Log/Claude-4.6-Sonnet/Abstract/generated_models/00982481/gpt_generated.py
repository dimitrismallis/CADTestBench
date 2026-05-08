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
        cyl_radius   = 10.0   # base cylinder radius
        cyl_height   = 30.0   # base cylinder height
        disk_radius  = 18.0   # larger circle radius (> cyl_radius)
        disk_z       = 25.0   # Z position where the disk starts (near top of cylinder)
        disk_height  = 5.0    # extrusion height of the disk
    
        # --- Step 1: Create and extrude the base cylinder ---
        # Centered at origin → spans Z from -15 to +15
        # We want it to span Z from 0 to cyl_height, so use centered=(True, True, False)
        base_cyl = (
            cq.Workplane("XY")
            .circle(cyl_radius)
            .extrude(cyl_height)   # extrudes upward; with default centered, spans -15 to +15
        )
        # Re-do with centered=False on Z so cylinder goes from Z=0 to Z=30
        base_cyl = (
            cq.Workplane("XY")
            .cylinder(cyl_height, cyl_radius, centered=(True, True, False))
        )
    
        # --- Step 2: Create a larger circle near the top of the cylinder ---
        # Place workplane at Z = disk_z (near top of cylinder, which ends at Z=30)
        # Extrude the disk upward by disk_height
        disk = (
            cq.Workplane(cq.Plane(origin=(0, 0, disk_z), normal=(0, 0, 1)))
            .circle(disk_radius)
            .extrude(disk_height)
        )
    
        # --- Step 3: Union the base cylinder and the disk ---
        result = base_cyl.union(disk)
    
        # --- Final object verification ---
        TOL = 0.1
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks:
        # X and Y span: disk is larger, radius=18 → total width = 36
        assert abs(bb.xlen - 2 * disk_radius) < TOL, \
            f"X extent: expected {2*disk_radius}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * disk_radius) < TOL, \
            f"Y extent: expected {2*disk_radius}, got {bb.ylen}"
    
        # Z span: cylinder from 0 to 30, disk from 25 to 30 (disk_z + disk_height = 30)
        expected_zlen = disk_z + disk_height  # = 30
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - expected_zlen) < TOL, \
            f"Z max: expected {expected_zlen}, got {bb.zmax}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z extent: expected {expected_zlen}, got {bb.zlen}"
    
        # Volume check:
        # Cylinder volume: π * r² * h = π * 10² * 30
        vol_cyl = math.pi * cyl_radius**2 * cyl_height
        # Disk volume: π * R² * h_disk = π * 18² * 5
        vol_disk_full = math.pi * disk_radius**2 * disk_height
        # Overlap (cylinder portion inside disk Z range): π * r² * (cyl_height - disk_z)
        overlap_height = cyl_height - disk_z  # = 5
        vol_overlap = math.pi * cyl_radius**2 * overlap_height
        expected_vol = vol_cyl + vol_disk_full - vol_overlap
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Cylindrical faces: base cylinder lateral + disk lateral = 2 cylindrical faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, \
            f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # Planar faces: bottom of cylinder (1) + annular ring at z=25 (1) + top of disk (1) = 3
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 3, \
            f"Planar faces: expected 3, got {planar_faces}"
    
        # Total faces = 5
        total_faces = result.faces().size()
        assert total_faces == 5, \
            f"Total faces: expected 5, got {total_faces}"
    
        # Symmetry: center of mass should be on Z axis (x≈0, y≈0)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"CoM X: expected ~0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected ~0, got {com.y}"
    
        # The disk radius is larger than the cylinder radius
        assert disk_radius > cyl_radius, \
            f"Disk radius {disk_radius} should be > cylinder radius {cyl_radius}"
    
        # Check that a point inside the cylinder (below disk) is inside the solid
        assert solid.isInside((0, 0, 10)), "Point (0,0,10) should be inside the cylinder"
        # Check that a point inside the disk (above disk_z) is inside the solid
        assert solid.isInside((15, 0, 27)), "Point (15,0,27) should be inside the disk"
        # Check that a point outside both is NOT inside
        assert not solid.isInside((15, 0, 10)), "Point (15,0,10) should be outside the solid"
    
        print(f"All assertions passed!")
        print(f"  Bounding box: X={bb.xlen:.2f}, Y={bb.ylen:.2f}, Z={bb.zlen:.2f}")
        print(f"  Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
        print(f"  Cylindrical faces: {cyl_faces}, Planar faces: {planar_faces}")
        print(f"  Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00982481/gpt_generated.stl')
