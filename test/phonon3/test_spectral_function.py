import numpy as np
from phono3py.phonon3.spectral_function import SpectralFunction

shifts = [
    -0.0049592, -0.0049592, -0.0120983, -0.1226471, -0.1214069, -0.1214069,
    -0.0051678, -0.0051678, -0.0128471, -0.1224616, -0.1200362, -0.1200362,
    -0.0055308, -0.0055308, -0.0122157, -0.1093754, -0.1077399, -0.1077399,
    -0.0037992, -0.0037992, -0.0089979, -0.0955525, -0.0958995, -0.0958995,
    -0.0034397, -0.0034397, -0.0107575, -0.1068741, -0.1067815, -0.1067815,
    -0.0017800, -0.0017800, -0.0102865, -0.1348585, -0.1275650, -0.1275650,
    0.0006728, 0.0006728, -0.0065349, -0.2011702, -0.2015991, -0.2015991,
    0.0021133, 0.0021133, 0.0020353, -0.0740009, -0.0833644, -0.0833644,
    0.0037739, 0.0037739, 0.0121357, 0.1597195, 0.1585307, 0.1585307,
    0.0026257, 0.0026257, 0.0103523, 0.1626420, 0.1634832, 0.1634832,
    -0.0189694, -0.0188985, -0.0415773, -0.0955391, -0.1180182, -0.1126508,
    -0.0194533, -0.0191057, -0.0420358, -0.0913521, -0.1140995, -0.1075009,
    -0.0233933, -0.0219600, -0.0466734, -0.0865867, -0.1086070, -0.1014454,
    -0.0140271, -0.0150165, -0.0344515, -0.0755416, -0.1018518, -0.0951606,
    -0.0058780, -0.0089457, -0.0256867, -0.0775726, -0.1070427, -0.1018654,
    -0.0069737, -0.0092857, -0.0333909, -0.1014042, -0.1320678, -0.1288315,
    -0.0030075, -0.0060858, -0.0245855, -0.1186313, -0.1963719, -0.1857004,
    0.0058243, 0.0030539, -0.0049966, -0.0583228, -0.0921850, -0.0893692,
    0.0141517, 0.0149365, 0.0312156, 0.0898626, 0.1454759, 0.1347802,
    0.0110954, 0.0137260, 0.0427527, 0.1280421, 0.1715647, 0.1648037]

spec_funcs = [
    0.0000000, 0.0000000, 0.0000000, 0.0000000, 0.0000000, 0.0000000,
    0.0029242, 0.0029242, 0.0009262, 0.0003634, 0.0003838, 0.0003838,
    0.0007678, 0.0007678, 0.0373760, 0.0010702, 0.0009678, 0.0009678,
    0.0008232, 0.0008232, 0.5674888, 0.0008545, 0.0008206, 0.0008206,
    0.0001065, 0.0001065, 0.0037537, 0.0005808, 0.0005891, 0.0005891,
    0.0003814, 0.0003814, 0.0112237, 0.0009503, 0.0011072, 0.0011072,
    0.0000917, 0.0000917, 0.0042648, 0.0014247, 0.0007688, 0.0007688,
    0.0001342, 0.0001342, 0.0053626, 0.0113299, 0.0112733, 0.0112733,
    0.0000221, 0.0000221, 0.0015374, 0.0059884, 0.0059895, 0.0059895,
    0.0000000, 0.0000000, 0.0000000, 0.0000000, 0.0000000, 0.0000000,
    0.0000000, 0.0000000, 0.0000000, 0.0000000, 0.0000000, 0.0000000,
    0.0010067, 0.0006160, 0.0003428, 0.0005280, 0.0004634, 0.0004811,
    0.0030157, 0.0012885, 0.0006403, 0.0007254, 0.0006859, 0.0006075,
    0.0783861, 0.0145968, 0.0040184, 0.0013955, 0.0010490, 0.0009551,
    0.1256767, 0.0076117, 0.0012648, 0.0005816, 0.0007186, 0.0005401,
    0.5288047, 0.0419927, 0.0032818, 0.0012094, 0.0010713, 0.0009373,
    0.0441985, 0.1523475, 0.0067098, 0.0029446, 0.0014789, 0.0015596,
    0.0267331, 30.4102899, 0.0090105, 0.0082343, 0.0118987, 0.0106408,
    0.0048560, 0.1573017, 0.0126811, 0.0085599, 0.0081138, 0.0077690,
    0.0000000, 0.0000000, 0.0000000, 0.0000000, 0.0000000, 0.0000000]


def test_SpectralFunction(si_pbesol):
    si_pbesol.mesh_numbers = [9, 9, 9]
    si_pbesol.init_phph_interaction()
    sf = SpectralFunction(si_pbesol.phph_interaction,
                          [1, 103],
                          temperatures=[300, ],
                          num_frequency_points=10)
    sf.run()
    # for line in sf.spectral_functions.reshape(-1, 6):
    #     print(("%.7f, " * 6) % tuple(line))
    # raise
    print(np.where(np.abs(spec_funcs - sf.spectral_functions.ravel()) > 1e-2))
    np.testing.assert_allclose(shifts, sf.shifts.ravel(), atol=1e-2)
    np.testing.assert_allclose(spec_funcs, sf.spectral_functions.ravel(),
                               atol=1e-2)
