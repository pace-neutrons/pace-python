struct my_data {
    double background;
    char *strdata;
    int intdata;
};

/* Functions which require their own-data-structure */
void user_model_init(void *model_data, double *p1, char *p2, int *p3);
void user_model_destroy(void *model_data);
void user_model_sqw(const double *qh, const double *qk, const double *ql, const double *en, const double *parameters, double *result, int *n_elem, void *owndata);
