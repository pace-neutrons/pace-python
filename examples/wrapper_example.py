from pace_python import Matlab
m = Matlab()
proj = m.projaxes([-0.5, 1, 0], [0, 0, 1], 'type', 'rrr')
w1 = m.cut_sqw('ei30_10K.sqw', proj, [0.1, 0.02, 0.5], [1.5, 2.5], [0.4, 0.5], [3, 0.5, 20])
w2 = w1.cut([0.1, 0.5], [3, 0.5, 20])
hf = w1.plot()
m.uiwait(hf)
