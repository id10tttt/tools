TARGET = multi_thread_get
OBJS = multi_thread_get.o

CC = gcc

CFLAGS = -c -g
LIBS = -lcurl -lpthread

$(TARGET) : $(OBJS)
	$(CC)  -o $(TARGET) $(OBJS) $(LIBS)

multi_thread_get.o : multi_thread_get.c
	$(CC) $(CFLAGS) $< $(LIBS)

clean:
	rm -rf $(TARGET) $(OBJS)
