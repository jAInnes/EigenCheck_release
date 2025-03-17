# Hauptprogramm
MAIN=main

# Alle Programme
OBJECTS=$(MAIN).o qr.o

# Welcher C-Compiler
CC=gcc
# Weitere zuschaltbare Optionen
CFLAGS=-Wall -fPIC

# Wo liegen die Headerdateien
INCDIR=-I. -I../lib

# Welcher Linker
LD=$(CC)
# Wo liegen die Bibliotheken
LIBDIR=../lib
# Weitere zuschaltbare Optionen
LDFLAGS=-Wl,-rpath=$(LIBDIR)

# Alle benötigten Bibliotheken
LDLIBS=-lmatrix_vector -lm

# Ziel des Makefiles
$(MAIN).out: $(OBJECTS) libmatrix_vector.so
	$(LD) -o $(MAIN).out $(OBJECTS) -L$(LIBDIR) $(LDLIBS) $(LDFLAGS)

# Ziel für das Erstellen der Bibliothek
libmatrix_vector.so:
	cd $(LIBDIR); make

# Wie erzeugt man C-Objektdateien
$(OBJECTS): %.o: %.c
	$(CC) $(INCDIR) -c $(CFLAGS) $< -o
