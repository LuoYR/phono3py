# Copyright (C) 2019 Atsushi Togo
# All rights reserved.
#
# This file is part of phono3py.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
# * Neither the name of the phonopy project nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import numpy as np
from phonopy.units import VaspToTHz
from phonopy.structure.symmetry import Symmetry
from phono3py.phonon3.joint_dos import JointDos
from phono3py.phonon.grid import BZGrid

from phono3py.file_IO import write_joint_dos


class Phono3pyJointDos(object):
    def __init__(self,
                 supercell,
                 primitive,
                 fc2,
                 mesh=None,
                 nac_params=None,
                 nac_q_direction=None,
                 sigmas=None,
                 cutoff_frequency=1e-4,
                 frequency_step=None,
                 num_frequency_points=None,
                 temperatures=None,
                 frequency_factor_to_THz=VaspToTHz,
                 frequency_scale_factor=None,
                 is_mesh_symmetry=True,
                 is_dense_gp_map=False,
                 symprec=1e-5,
                 output_filename=None,
                 log_level=0):
        if sigmas is None:
            self._sigmas = [None]
        else:
            self._sigmas = sigmas
        self._temperatures = temperatures
        self._is_mesh_symmetry = is_mesh_symmetry
        self._filename = output_filename
        self._log_level = log_level

        symmetry = Symmetry(primitive, symprec)
        self._bz_grid = BZGrid(mesh,
                               lattice=primitive.cell,
                               primitive_symmetry=symmetry,
                               is_dense_gp_map=is_dense_gp_map)

        self._jdos = JointDos(
            primitive,
            supercell,
            self._bz_grid,
            fc2,
            nac_params=nac_params,
            nac_q_direction=nac_q_direction,
            cutoff_frequency=cutoff_frequency,
            frequency_step=frequency_step,
            num_frequency_points=num_frequency_points,
            temperatures=self._temperatures,
            frequency_factor_to_THz=frequency_factor_to_THz,
            frequency_scale_factor=frequency_scale_factor,
            is_mesh_symmetry=self._is_mesh_symmetry,
            is_dense_gp_map=is_dense_gp_map,
            symprec=symprec,
            filename=output_filename,
            log_level=self._log_level)

        self._joint_dos = None

    @property
    def grid(self):
        return self._bz_grid

    def run(self, grid_points, write_jdos=False):
        if self._log_level:
            print("--------------------------------- Joint DOS "
                  "---------------------------------")
            print("Sampling mesh: [ %d %d %d ]" % tuple(self._bz_grid.D_diag))

        for i, gp in enumerate(grid_points):
            self._jdos.set_grid_point(gp)

            if self._log_level:
                weights = self._jdos.get_triplets_at_q()[1]
                print("======================= "
                      "Grid point %d (%d/%d) "
                      "======================="
                      % (gp, i + 1, len(grid_points)))
                adrs = self._jdos.bz_grid.addresses[gp]
                q = np.dot(adrs, self._bz_grid.QDinv.T)
                print("q-point: (%5.2f %5.2f %5.2f)" % tuple(q))
                print("Number of triplets: %d" % len(weights))
                print("Frequency")
                for f in self._jdos.get_phonons()[0][gp]:
                    print("%8.3f" % f)

            if not self._sigmas:
                raise RuntimeError("sigma or tetrahedron method has to be set.")

            for sigma in self._sigmas:
                if self._log_level:
                    if sigma is None:
                        print("Tetrahedron method is used.")
                    else:
                        print("Smearing method with sigma=%s is used." % sigma)
                self._jdos.set_sigma(sigma)
                self._jdos.run()

                if write_jdos:
                    filename = self._write(gp, sigma=sigma)
                    if self._log_level:
                        print("JDOS is written into \"%s\"." % filename)

    @property
    def dynamical_matrix(self):
        return self._jdos.dynamical_matrix

    @property
    def frequency_points(self):
        return self._jdos.frequency_points

    @property
    def joint_dos(self):
        return self._jdos.joint_dos

    def _write(self, gp, sigma=None):
        return write_joint_dos(gp,
                               self._bz_grid.D_diag,
                               self._jdos.frequency_points,
                               self._jdos.joint_dos,
                               sigma=sigma,
                               temperatures=self._temperatures,
                               filename=self._filename,
                               is_mesh_symmetry=self._is_mesh_symmetry)
