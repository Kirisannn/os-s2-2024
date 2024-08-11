#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void catchHUP(int sig) {
    printf("Ouch!\n");
}

void catchINT(int sig) {
    printf("Yeah!\n");
}

int main(int argc, char *argv[]) {
    signal(SIGHUP, catchHUP);
    signal(SIGINT, catchINT);
    char *input = argv[1];
    int n = atoi(input);
    for (int i = 0; i < n; i++) {
        printf("%d\n", i * 2);
        sleep(5);
    }

    return 0;
}