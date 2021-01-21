from pace_python import Matlab
m = Matlab()

from matlab import double as md
import numpy as np

af = m.sw_model('squareAF', 1.)
qs = ([0, 0, 0], [1, -1, 1], [1, 1, 0], [1, 0, 0.5], [0, 1, 0], [0, 0.5, 0], [1, 0, 0], [0.5, 0, 1], [0, 0, 0], 200)
spec = af.spinwave(qs)
sped = af.spinwave(qs, 'use_brille', True, 'node_volume_fraction', 1.e-4)
spee = af.spinwave(qs, 'use_brille', True, 'use_vectors', True, 'node_volume_fraction', 1.e-4)
spec = m.sw_egrid(m.sw_neutron(spec), 'Evect', np.linspace(0, 50, 200))
sped = m.sw_egrid(m.sw_neutron(sped), 'Evect', np.linspace(0, 50, 200))
spee = m.sw_egrid(m.sw_neutron(spee), 'Evect', np.linspace(0, 50, 200))

hf0 = m.figure()
m.subplot(311); m.sw_plotspec(spec); m.legend('off'); m.title('SpinW')
m.subplot(312); m.sw_plotspec(sped); m.legend('off'); m.title('Interpolated Sab')
m.subplot(313); m.sw_plotspec(spee); m.legend('off'); m.title('Interpolated Eigenvectors')
m.uiwait(hf0)
