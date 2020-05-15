/* Functions which don't require an own-data-structure */
void user_model_sqw(const double *qh, const double *qk, const double *ql, const double *en, const double *parameters, double *result, int *n_elem, int *own_memory);
/*
void user_model_dsp(const double *qh, const double *qk, const double *ql, const double *parameters, double *result_omega, double *result_S, int n_elem, bool own_memory=false);
void user_model_pow(const double *modQ, const double *en, const double *parameters, double *result, int n_elem, bool own_memory=false);
void user_model_1d(const double *en, const double *parameters, double *result, int n_elem, bool own_memory=false);
void user_model_0d(const double *parameters, double *result, int n_elem, bool own_memory=false);
*/
/* Functions which require their own-data-structure */
/*
void user_model_init(void *model_data);
void user_model_destroy(void *model_data);
void user_model_init(void *model_data, double *result, int n_elem);
void user_model_destroy(void *model_data, double *result);
void user_model_sqw(const double *qh, const double *qk, const double *ql, const double *en, const double *parameters, double *result, void *model_data, int n_elem, bool own_memory=false);
void user_model_dsp(const double *qh, const double *qk, const double *ql, const double *parameters, double *result_omega, double *result_S, void *model_data, int n_elem, bool own_memory=false);
void user_model_dsp(const double *modQ, const double *en, const double *parameters, double *result, void *model_data, int n_elem, bool own_memory=false);
void user_model_1d(const double *en, const double *parameters, double *result, void *model_data, int n_elem, bool own_memory=false);
void user_model_0d(const double *parameters, double *result, void *model_data, int n_elem, bool own_memory=false);
*/
