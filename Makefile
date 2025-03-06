# Hauptprogramm
MAIN=main

# Alle C-Quellcodes und Objektdateien
SRC=$(MAIN).c ausgabe.c matrix_vector.c $(wildcard uploads/*.c)
OBJECTS=$(SRC:.c=.o)

# Welcher C-Compiler
CC=gcc
# CC=icc
# Weitere zuschaltbare Optionen
CCFLAGS=-O -Wall
# Alternativ Debugger-Informationen generieren
#CCFLAGS=-g

# Wo liegen die Headerdateien
INCDIR=-I.

# Welcher Linker
LD=$(CC)
# Weitere zuschaltbare Optionen
LDFLAGS=-O
# Wo liegen die Bibliotheken
LIBDIR=

# Alle benötigten Bibliotheken
LIBS= -lm

# Name der Input-Datei
INPUT_FILE=aufgabe2.dat

# Name der Datei mit den erwarteten Ergebnissen
EXPECTED_FILE=expected.txt

# Ziel des Makefiles
$(MAIN).out: $(OBJECTS)
	$(LD) -o $(MAIN).out $(OBJECTS) $(LIBDIR) $(LIBS)
	./$(MAIN).out $(INPUT_FILE) $(EXPECTED_FILE)

# Wie erzeugt man C-Objektdateien
$(OBJECTS): %.o: %.c
	$(CC) $(INCDIR) -c $(CCFLAGS) $< -o $@

clean:
	rm -f *.o
	rm -f *.out
