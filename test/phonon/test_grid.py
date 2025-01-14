import numpy as np
from phonopy.structure.tetrahedron_method import TetrahedronMethod
from phono3py.phonon.grid import (get_grid_point_from_address,
                                  get_grid_point_from_address_py, BZGrid)


def test_get_grid_point_from_address(agno2_cell):
    """

    Compare get_grid_point_from_address from spglib and that
    written in python with mesh numbers.

    """

    mesh = (10, 10, 10)

    for address in list(np.ndindex(mesh)):
        gp_spglib = get_grid_point_from_address(address, mesh)
        gp_py = get_grid_point_from_address_py(address, mesh)
        # print("%s %d %d" % (address, gp_spglib, gp_py))
        np.testing.assert_equal(gp_spglib, gp_py)


def test_BZGrid(si_pbesol_111):
    """Basis test of BZGrid type1 and type2"""

    lat = si_pbesol_111.primitive.cell
    reclat = np.linalg.inv(lat)
    mesh = [4, 4, 4]

    gp_map2 = [0, 1, 2, 4, 5, 6, 7, 8, 9, 11, 12, 14, 15, 16, 17, 18,
               19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 34, 35,
               36, 40, 41, 43, 44, 46, 47, 48, 49, 50, 54, 56, 57, 59,
               60, 61, 65, 66, 67, 68, 69, 70, 71, 72, 73, 77, 78, 79,
               83, 84, 85, 86, 87, 88, 89]

    bzgrid1 = BZGrid(mesh, lattice=lat, is_dense_gp_map=False)
    bzgrid2 = BZGrid(mesh, lattice=lat, is_dense_gp_map=True)

    adrs1 = bzgrid1.addresses[:np.prod(mesh)]
    adrs2 = bzgrid2.addresses[bzgrid2.gp_map[:-1]]
    assert ((adrs1 - adrs2) % mesh == 0).all()
    np.testing.assert_equal(bzgrid1.addresses.shape, bzgrid2.addresses.shape)
    # print("".join(["%d, " % i for i in bzgrid2.gp_map.ravel()]))
    np.testing.assert_equal(bzgrid2.gp_map.ravel(), gp_map2)

    dist1 = np.sqrt((np.dot(adrs1, reclat.T) ** 2).sum(axis=1))
    dist2 = np.sqrt((np.dot(adrs2, reclat.T) ** 2).sum(axis=1))
    np.testing.assert_allclose(dist1, dist2, atol=1e-8)


def test_BZGrid_bzg2grg(si_pbesol_111):
    """BZGrid to GRGrid

    This mapping table is stored in BZGrid, but also determined by
    get_grid_point_from_address. This test checks the consistency.

    """

    lat = si_pbesol_111.primitive.cell
    mesh = [4, 4, 4]
    bzgrid1 = BZGrid(mesh, lattice=lat, is_dense_gp_map=False)
    grg = []
    for i in range(len(bzgrid1.addresses)):
        grg.append(get_grid_point_from_address(bzgrid1.addresses[i], mesh))
    np.testing.assert_equal(grg, bzgrid1.bzg2grg)

    bzgrid2 = BZGrid(mesh, lattice=lat, is_dense_gp_map=True)
    grg = []
    for i in range(len(bzgrid2.addresses)):
        grg.append(get_grid_point_from_address(bzgrid2.addresses[i], mesh))
    np.testing.assert_equal(grg, bzgrid2.bzg2grg)


def test_BZGrid_SNF(si_pbesol_111):
    """SNF in BZGrid"""
    lat = si_pbesol_111.primitive.cell
    mesh = 10
    bzgrid1 = BZGrid(mesh,
                     lattice=lat,
                     primitive_symmetry=si_pbesol_111.primitive_symmetry,
                     is_dense_gp_map=False)
    _test_BZGrid_SNF(bzgrid1)

    bzgrid2 = BZGrid(mesh,
                     lattice=lat,
                     primitive_symmetry=si_pbesol_111.primitive_symmetry,
                     is_dense_gp_map=True)
    _test_BZGrid_SNF(bzgrid2)


def _test_BZGrid_SNF(bzgrid):
    # from phonopy.structure.atoms import PhonopyAtoms
    # from phonopy.interface.vasp import get_vasp_structure_lines

    A = bzgrid.grid_matrix
    D_diag = bzgrid.D_diag
    P = bzgrid.P
    Q = bzgrid.Q
    np.testing.assert_equal(np.dot(P, np.dot(A, Q)), np.diag(D_diag))

    # print(D_diag)
    # grg2bzg = bzgrid.grg2bzg
    # qpoints = np.dot(bzgrid.addresses[grg2bzg], bzgrid.QDinv.T)
    # cell = PhonopyAtoms(cell=np.linalg.inv(lat).T,
    #                     scaled_positions=qpoints,
    #                     numbers=[1,] * len(qpoints))
    # print("\n".join(get_vasp_structure_lines(cell)))

    gr_addresses = bzgrid.addresses[bzgrid.grg2bzg]
    # print(D_diag)
    # print(len(gr_addresses))
    # for line in gr_addresses.reshape(-1, 12):
    #     print("".join(["%d, " % i for i in line]))

    ref = [0, 0, 0, -1, 0, 0, 0, 1, 0, 1, 1, 0,
           0, -2, 0, -1, -2, 0, 0, -1, 0, -1, -1, 0,
           0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1,
           0, 2, 1, 1, 2, 1, 0, -1, 1, -1, -1, 1,
           0, 0, -2, -1, 0, -2, 0, 1, 2, 1, 1, 2,
           0, -2, -2, -1, -2, -2, 0, -1, -2, -1, -1, -2,
           0, 0, -1, -1, 0, -1, 0, 1, -1, -1, 1, -1,
           0, -2, -1, -1, -2, -1, 0, -1, -1, -1, -1, -1]

    assert (((np.reshape(ref, (-1, 3)) - gr_addresses)
            % bzgrid.D_diag).ravel() == 0).all()

    ref_rots = [
        1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 2, 1, -1, 2, 2, -1,
        1, 0, 0, 2, -1, 0, 4, 0, -1, 1, 0, 0, 0, -1, 1, 2, -2, 1,
        -1, 0, 0, 0, -1, 0, -2, -2, 1, -1, 0, 0, 0, 1, -1, 0, 0, -1,
        -1, 0, 0, -2, 1, 0, -2, 2, -1, -1, 0, 0, -2, -1, 1, -4, 0, 1,
        -1, -1, 1, 0, -1, 1, -2, -1, 2, -1, -1, 1, 0, -2, 1, 0, -3, 2,
        -1, -1, 1, -2, -1, 1, -2, -3, 2, -1, -1, 1, -2, 0, 1, -4, -1, 2,
        1, 1, -1, 0, 1, -1, 0, 3, -2, 1, 1, -1, 2, 0, -1, 2, 1, -2,
        1, 1, -1, 2, 1, -1, 4, 1, -2, 1, 1, -1, 0, 2, -1, 2, 3, -2,
        -1, 1, 0, -2, 0, 1, -2, 1, 1, -1, 1, 0, -2, 1, 0, -4, 1, 1,
        -1, 1, 0, 0, 2, -1, -2, 3, -1, -1, 1, 0, 0, 1, 0, 0, 3, -1,
        1, -1, 0, 2, 0, -1, 4, -1, -1, 1, -1, 0, 0, -1, 0, 2, -1, -1,
        1, -1, 0, 0, -2, 1, 0, -3, 1, 1, -1, 0, 2, -1, 0, 2, -3, 1,
        -1, 0, 0, 0, -1, 0, 0, 0, -1, -1, 0, 0, -2, -1, 1, -2, -2, 1,
        -1, 0, 0, -2, 1, 0, -4, 0, 1, -1, 0, 0, 0, 1, -1, -2, 2, -1,
        1, 0, 0, 0, 1, 0, 2, 2, -1, 1, 0, 0, 0, -1, 1, 0, 0, 1,
        1, 0, 0, 2, -1, 0, 2, -2, 1, 1, 0, 0, 2, 1, -1, 4, 0, -1,
        1, 1, -1, 0, 1, -1, 2, 1, -2, 1, 1, -1, 0, 2, -1, 0, 3, -2,
        1, 1, -1, 2, 1, -1, 2, 3, -2, 1, 1, -1, 2, 0, -1, 4, 1, -2,
        -1, -1, 1, 0, -1, 1, 0, -3, 2, -1, -1, 1, -2, 0, 1, -2, -1, 2,
        -1, -1, 1, -2, -1, 1, -4, -1, 2, -1, -1, 1, 0, -2, 1, -2, -3, 2,
        1, -1, 0, 2, 0, -1, 2, -1, -1, 1, -1, 0, 2, -1, 0, 4, -1, -1,
        1, -1, 0, 0, -2, 1, 2, -3, 1, 1, -1, 0, 0, -1, 0, 0, -3, 1,
        -1, 1, 0, -2, 0, 1, -4, 1, 1, -1, 1, 0, 0, 1, 0, -2, 1, 1,
        -1, 1, 0, 0, 2, -1, 0, 3, -1, -1, 1, 0, -2, 1, 0, -2, 3, -1]

    np.testing.assert_equal(ref_rots, bzgrid.rotations.ravel())


def test_SNF_tetrahedra_relative_grid(aln_lda):
    """Check if relative grid q-points agree with points around microzone.

    Compare between microzone and primitive lattices in
    reciprocal Cartesian coordinates.

    """

    aln_lda.mesh_numbers = 25
    bz_grid = aln_lda.grid
    plat = np.linalg.inv(aln_lda.primitive.cell)
    mlat = bz_grid.microzone_lattice
    bz_grid._generate_grid(25, force_SNF=True)
    thm = TetrahedronMethod(mlat)
    snf_tetrahedra = np.dot(thm.get_tetrahedra(), bz_grid.P.T)

    np.testing.assert_equal(bz_grid.D_diag, [2, 8, 24])

    for mtet, ptet in zip(thm.get_tetrahedra(), snf_tetrahedra):
        np.testing.assert_allclose(
            np.dot(mtet, mlat.T),
            np.dot(np.dot(ptet, bz_grid.QDinv.T), plat.T),
            atol=1e-8)
        # print(np.dot(mtet, mlat.T))
        # print(np.dot(np.dot(ptet, bz_grid.QDinv.T), plat.T))
