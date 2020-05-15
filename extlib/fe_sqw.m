function out = fe_sqw(h, k, l, e, p)

js = p(1);
d = p(2);

om = d + (8*js) .* (1 - cos(pi * h) .* cos(pi * k) .* cos(pi * l));
q2 = ((1/(2*2.87)).^2) * (h.^2 + k.^2 + l.^2);

% The magnetic form factor of Fe2+
A=0.0706; a=35.008;  B=0.3589; b=15.358;  C=0.5819; c=5.561;  D=-0.0114;
ff = A * exp(-a*q2) + B * exp(-b*q2) + C * exp(-c*q2) + D;

out = (ff.^2) .* (p(5)/pi) .* (e ./ (1-exp(-11.602*e/p(4)))) .* (4 * p(3) * om) ./ ((e.^2 - om.^2).^2 + 4*(p(3) * e).^2);
disp(size(out))
