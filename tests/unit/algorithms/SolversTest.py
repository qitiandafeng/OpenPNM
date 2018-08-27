import openpnm as op
import scipy as sp
import importlib
import numpy.testing as nt
sp.random.seed(1)


class SolversTest:

    def setup_class(self):
        self.net = op.network.Cubic(shape=[10, 10, 10])
        self.geom = op.geometry.StickAndBall(network=self.net,
                                             pores=self.net.Ps,
                                             throats=self.net.Ts)
        self.phase = op.phases.GenericPhase(network=self.net)
        self.phys = op.physics.GenericPhysics(network=self.net,
                                              phase=self.phase,
                                              geometry=self.geom)
        self.phys['throat.conductance'] = sp.random.rand(self.net.Nt)
        self.alg = op.algorithms.GenericTransport(network=self.net)
        self.alg.settings.update(quantity='pore.x',
                                 conductance='throat.conductance')
        self.alg.setup(phase=self.phase)
        self.alg.set_value_BC(pores=self.net.pores('left'), values=1.0)
        self.alg.set_value_BC(pores=self.net.pores('bottom'), values=0.0)

    def test_scipy_direct(self):
        solvers = ['spsolve']
        for solver in solvers:
            self.alg.settings['solver'] = solver
            self.alg.run()
            xmean = self.alg['pore.x'].mean()
            nt.assert_allclose(actual=xmean, desired=0.47766957)

    def test_scipy_iterative(self):
        solvers = ['bicg', 'bicgstab', 'cg', 'cgs', 'qmr', 'gcrotmk', 'gmres',
                   'lgmres', 'minres']
        for solver in solvers:
            self.alg.settings['solver'] = solver
            self.alg.run()
            xmean = self.alg['pore.x'].mean()
            nt.assert_allclose(actual=xmean, desired=0.47766957)

    def test_scipy_iterative_diverge(self):
        solvers = ['bicg', 'bicgstab', 'cg', 'cgs', 'qmr', 'gcrotmk', 'gmres',
                   'lgmres', 'minres']
        self.alg.settings['solver'] = {'family': 'scipy', 'maxiter': 1}
        for solver in solvers:
            self.alg.settings['solver']['solver'] = solver
            with nt.assert_raises(Exception):
                self.alg.run()
        self.alg.settings['solver'].update(maxiter=100)

    def test_pyamg(self):
        self.alg.settings['solver'] = 'pyamg'
        self.alg.run()
        xmean = self.alg['pore.x'].mean()
        nt.assert_allclose(actual=xmean, desired=0.47766957)

    def test_petsc(self):
        self.alg.settings['solver'] = 'petsc'
        if importlib.util.find_spec('petsc4py') is None:
            with nt.assert_raises(Exception):
                self.alg.run()
        else:
            self.alg.run()
            xmean = self.alg['pore.x'].mean()
            nt.assert_allclose(actual=xmean, desired=0.47766957)


if __name__ == '__main__':
    t = SolversTest()
    t.setup_class()
    for item in t.__dir__():
        if item.startswith('test'):
            print('running test: '+item)
            t.__getattribute__(item)()
    self = t
