#include<stdio.h>
#include<stdlib.h>
#include "matrix_vector.h"

#define LINEBUF 256

double* new_vector(int n) {
    double* v;
   // printf("n*(double) = %ld\n", n*sizeof(double));
    v = (double *) malloc(n * sizeof(double));
    return v;
}

double** new_matrix(int n) {
    double **mat;
    int j;
   // printf("n*(double*) = %ld\n", n*sizeof(double*));

    mat = (double **) malloc(n*sizeof(double* ));
    if(mat == NULL) return NULL;

    for (j=0; j<n; j++) {
        mat[j] = (double* ) malloc(n*sizeof(double));
        if(mat[j] == NULL) return NULL;
    }

    return mat;
}

void free_matrix(double **mat, int n) {
    int i;
    for(i = 0; i < n; i++)
        free(mat[i]);
    free(mat);
}

double* read_vector(FILE *inputfile, int n) {
    int i;
    double *b; 
    b = new_vector(n);

    if (b == NULL) return NULL;
    /* Lese elemente für b ein */
    for (i = 0; i < n; i++ ) 
    {
        fscanf(inputfile,"%lf", &(b[i]) );
        printf("%f   ",b[i]);
    }
    printf("\n");

    return b;
}

double** read_matrix(FILE *inputfile, int *n) {
    int i, j;
    double **a = NULL;
    char buf[LINEBUF];
    int num_lines = 0;

    if (inputfile == NULL) {
        fprintf(stderr, "Fehler: Datei-Pointer ist NULL\n");
        return NULL;
    }

    // Ermittle die Dimension der Matrix durch Zählen der Zeilen
    while (fgets(buf, LINEBUF, inputfile) != NULL) {
        num_lines++;
    }
    *n = num_lines - 1; // Erste Zeile wird übersprungen
    printf("Matrixdimension ermittelt: %d\n", *n);

    rewind(inputfile); // Setze den Dateipointer an den Anfang der Datei

    // Allokiere Speicher für die Matrix
    a = new_matrix(*n);
    if (a == NULL) {
        fprintf(stderr, "Fehler bei der Speicherallokation für die Matrix\n");
        return NULL;
    }

    // Erste Zeile wird übersprungen
    for (i = 0; i < *n; i++) {
        for (j = 0; j < *n; j++) {
            if (fscanf(inputfile, "%lf", &(a[i][j])) != 1) {
                fprintf(stderr, "Fehler beim Lesen des Elements a[%d][%d]\n", i, j);
                free_matrix(a, *n);
                return NULL;
            }
           // printf("Element a[%d][%d] gelesen: %10.5f\n", i, j, a[i][j]);  // Debug-Ausgabe
        }
    }
    return a;
}