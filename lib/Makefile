# Alle Programme
SOURCES= $(wildcard *.c)
OBJECTS= $(patsubst %.c,%.o,$(SOURCES)) 

# Welcher C-Compiler
CC=gcc
# CC=icc
# Weitere zuschaltbare Optionen
CFLAGS=-fPIC
# Alternativ Debugger-Informationen generieren
#CCFLAGS=-g

# Wo liegen die Headerdateien
INCDIR=-I.

# Welcher Linker
LD=ld
# Weitere zuschaltbare Optionen
LDFLAGS=-shared
# Wo liegen die Bibliotheken
LIBDIR=

# Alle benötigten Bibliotheken
#LDLIBS= -lm 
LIB=libmatrix_vector.so

# Ziel des Makefiles
lib: $(OBJECTS) 
	$(LD) $(LDFLAGS) $(OBJECTS) $(LIBDIR) -o $(LIB)

# Wie erzeugt man C-Objektdateien
$(OBJECTS): %.o: %.c
	$(CC) $(INCDIR) -c $(CFLAGS) $< -o $@

clean:
	-rm *.o
	-rm $(LIB)
