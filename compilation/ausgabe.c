#include "ausgabe.h"

void print_vector(double *v, int n)
{
   int i;

   for(i = 0; i < n; i++)
   {
      printf("%10.5f", v[i]);
      printf("\n");
   }
}

void print_matrix(double **a, int n)
{
   int i, j;

   for(i = 0; i < n; i++)
   {
      printf("i = %d", i);
      for(j = 0; j < n; j++)
      {
         printf("%10.5f", a[i][j]);
      }
      printf("\n");
   }
}


