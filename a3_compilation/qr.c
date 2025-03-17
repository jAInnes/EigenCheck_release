#include<stdio.h>
#include<math.h>
#include<stdlib.h>
#include"matrix_vector.h"

void rueckwarts_einsetzen(double **a, double *b, double *x, int n, int m)
{
   for ( int i = m - 1; i >= 0; i-- )
   {
      for ( int j = i + 1; j < n; j++ )
      {
         b[i] = b[i] - a[i][j] * x[j];
      }
      x[i] = b[i] / a[i][i];
   }
}

void qr(double **a, double *b, double *x, int m, int n)
{
   int i,j,k;
   
   // Berechnung von Q_ji * A
   for ( i = 0; i < n; i++ )
   {
      for ( j = i + 1; j < m; j++ )
      {
         if ( fabs(a[j][i]) > 1e-8)
         {
            double t = 1. / sqrt( pow(a[i][i], 2.) + pow(a[j][i], 2.) );
	        double s = t * a[j][i];
            double c = t * a[i][i];

            for(k = i; k < n; k++)
            {
               t = c * a[i][k] + s * a[j][k];
               if ( k != i )
               {
                  a[j][k] = -s * a[i][k] + c * a[j][k];
               }
		       a[i][k] = t;
            }
            a[j][i] = 0.;

            t = c * b[i] + s * b[j];
            b[j] = -s * b[i] + c * b[j];
			b[i] = t;

            print_matrix(a, m, n);
            printf("\n");
            print_vector(b, m);
            printf("\n");
         }
      }
   }
}

