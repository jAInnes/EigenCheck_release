#include<stdio.h>
#include<math.h>
#include<stdlib.h>

void vorwarts_elimination(double **a, double *b, double *x, int n)
{
   int k, i;

   for(k = 0; k < n; k++)
   {
      for(i = 0; i < k; i++)
      {
         b[k] = b[k] - a[k][i] * b[i];
      }
      b[k] = b[k] / a[k][k];
   }
}

void rueckwarts_elimination(double **a, double *b, double *x, int n)
{
   int k, i;

   for(k = n - 1; k > - 1; k--)
   {
      for(i = k + 1; i < n; i++)
      {
         b[k] = b[k] - a[i][k] * x[i];
      }
      x[k] = b[k] / a[k][k]; 
   }
}

void cholesky(double **a, double *b, double *x, int n)
{
   int i,j,k;

   for(k = 0; k < n; k++)
   {
      for(j = 0; j < k; j++)
      {
         a[k][k] = a[k][k] - a[k][j] * a[k][j];  
      }
      a[k][k] = sqrt(a[k][k]);

      for(i = k + 1; i < n; i++)
      {
         for(j = 0; j < k; j++)
         {
            a[i][k] = a[i][k] - a[i][j] * a[k][j];
         }
         a[i][k] = a[i][k] / a[k][k];
      }
   }
   vorwarts_elimination(a,b,x,n);
   rueckwarts_elimination(a,b,x,n);
}

