#include<stdio.h>
#include<math.h>
#include<stdlib.h>
#include<matrix_vector.h>
#include<cholesky.h>
#include<ausgabe.h>

int main (int argc, char* argv[])
{
   int n,m;

//   char *dateiname = "aufgabe2.dat";
   double **a;
   double *b, *x;
   FILE *datei = 0;

   if(argc > 1)
   {
	   datei = fopen(argv[1], "r");
   }
   else
   {
	   printf("Datei muss übergeben werden!\n");
	   return 255;
   }
   
   a = read_matrix(datei, &n);
   printf("%p   \n", a);
   if(a == NULL) return 1;

   b = read_vector(datei, n);
   if(b == NULL) return 2;

   x = new_vector(n);
   if(x == NULL) return 3;

   cholesky(a, b, x, n);
   printf("\nNach Cholesky-Zerlegung:\n");
   print_matrix(a, n);
   printf("\nLoesung:\n");
   print_vector(x, n);
   printf("\n");
   
   free_matrix(a, n);
   free(b);
   free(x);

   return 0;
}

