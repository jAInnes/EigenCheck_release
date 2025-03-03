double* new_vector(int n);
double** new_matrix(int n);
void free_matrix(double **mat, int n);
double* read_vector(FILE *inputfile, int n);
double** read_matrix(FILE *inputfile, int *n);
