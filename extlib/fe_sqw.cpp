#include <cmath>

extern "C" {

void user_model_sqw(const double *qh, const double *qk, const double *ql, const double *en, const double *parameters, double *result, int *n_elem)
{
/*
def py_fe_sqw(h, k, l, e, p):
    js = p[0]
    d = p[1]
    om = d + (8*js) * (1 - np.cos(np.pi * h) * np.cos(np.pi * k) * np.cos(np.pi * l))
    q2 = ((1/(2*2.87))**2) * (h**2 + k**2 + l**2)
    # The magnetic form factor of Fe2+
    A=0.0706; a=35.008;  B=0.3589; b=15.358;  C=0.5819; c=5.561;  D=-0.0114;
    ff = A * np.exp(-a*q2) + B * np.exp(-b*q2) + C * np.exp(-c*q2) + D
    return (ff**2) * (p[4]/np.pi) * (e / (1-np.exp(-11.602*e/p[3]))) * (4 * p[2] * om) / ((e**2 - om**2)**2 + 4*(p[2] * e)**2)
*/
    const double js = parameters[0];
    const double d = parameters[1];
    const double gam = parameters[2];
    const double tt = parameters[3];
    const double amp = parameters[4] / M_PI;
    const double js8 = 8 * js;
    const double qscal = pow(1./(2.*2.87), 2.);
    const double A=0.0706, a=35.008, B=0.3589, b=15.358, C=0.5819, c=5.561, D=-0.0114;

    double om, q2, ff, e2om2, game;
    for (int i=0; i<*n_elem; i++) {
        om = d + js8 * (1. - cos(M_PI * qh[i]) * cos(M_PI * qk[i]) * cos(M_PI * ql[i]));
        q2 = qscal * (qh[i]*qh[i] + qk[i]*qk[i] + ql[i]*ql[i]);
        ff = A * exp(-a * q2) + B * exp(-b * q2) + C * exp(-c * q2) + D;
        e2om2 = (en[i]*en[i] - om*om);
        game = gam * en[i];
        result[i] = (ff * ff) * amp * (en[i] / (1 - exp(-11.602*en[i] / tt))) * (4 * gam * om) / (e2om2*e2om2 + 4 * game * game);
    }

}

}
