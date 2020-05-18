#include <math.h>
#include <stdio.h>
#include "extlib_struct.h"

void user_model_sqw(const double *qh, const double *qk, const double *ql, const double *en, const double *parameters, double *result, int *n_elem, void *owndata)
{
    const double js = parameters[0];
    const double d = parameters[1];
    const double gam = parameters[2];
    const double tt = parameters[3];
    const double amp = parameters[4] / M_PI;
    const double js8 = 8 * js;
    const double qscal = pow(1./(2.*2.87), 2.);
    const double A=0.0706, a=35.008, B=0.3589, b=15.358, C=0.5819, c=5.561, D=-0.0114;

    const double bkg = ((struct my_data*)owndata)->background;
    const char* strdat = ((struct my_data*)owndata)->strdata;
    /* printf("%s\n", strdat); */

    double om, q2, ff, e2om2, game;
    for (int i=0; i<*n_elem; i++) {
        om = d + js8 * (1. - cos(M_PI * qh[i]) * cos(M_PI * qk[i]) * cos(M_PI * ql[i]));
        q2 = qscal * (qh[i]*qh[i] + qk[i]*qk[i] + ql[i]*ql[i]);
        ff = A * exp(-a * q2) + B * exp(-b * q2) + C * exp(-c * q2) + D;
        e2om2 = (en[i]*en[i] - om*om);
        game = gam * en[i];
        result[i] = ((ff * ff) * amp * (en[i] / (1 - exp(-11.602*en[i] / tt))) * (4 * gam * om) / (e2om2*e2om2 + 4 * game * game)) + bkg;
    }

}

