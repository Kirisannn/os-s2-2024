/*********************************************************************
   Program  : miniShell                   Version    : 1.3
 --------------------------------------------------------------------
   skeleton code for linix/unix/minix command line interpreter
 --------------------------------------------------------------------
   File			: minishell.c
   Compiler/System	: gcc/linux

********************************************************************/

#include <sys/types.h>
#include <sys/wait.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <signal.h>

#define NV 20   // max number of command tokens
#define NL 100  // max length of command line

char line[NL];           // command line buffer
int ampersand = 0;       // background indicator
int ampersandCount = 0;  // background processes count
int pids[NV];            // array of process ids
char *bgProcesses[NV];   // array of pointers to background processes
char currBgProcess[NL];  // current background process for temporary storage

// Shell prompt
void prompt(void) {
    fprintf(stdout, "\n msh> ");
    fflush(stdout);
}

// Helper function for correctly terminating child processes if execvp fails
// https://www.gnu.org/software/libc/manual/html_node/Process-Completion.html
void catchChild(int sig) {
    int pid, status;  // Store the PID and status of the child process

    // Wait for the child process to terminate
    while (1) {                               // Check forever
        pid = waitpid(-1, &status, WNOHANG);  // Wait for any child process to terminate
        if (pid <= 0) {                       // Base case: If no child process is found
            break;
        }

        // Case: If child is currently executing
        if (pid == 0) {
            break;
        }

        // Case: If child process is terminated, print the PID and '...done'
        for (int i = 0; i < ampersandCount; i++) {
            if (pids[i + 1] == pid) {  // If the PID matches the child process
                printf("[%d] %s done\n", i + 1, bgProcesses[i + 1]);
                fflush(stdout);
                // Free the memory allocated to the background process
                free(bgProcesses[i + 1]);
            }
        }
    }
}

// argk: number of command line arguments
// argv: array of pointers to command line arguments
// envp: array of pointers to environment strings
int main(int argk, char *argv[], char *envp[]) {
    int frkRtnVal;        // return value from fork
    int wpid;             // return value from wait
    char *v[NV];          // array of pointers to command line tokens
    char *sep = " \t\n";  // token separators - space, tab, newline (delimiters)
    int i;                // loop counter

    // Signal handler for catching child processes
    if (signal(SIGCHLD, catchChild) == SIG_ERR) {
        perror("Signal handler failed");
    }

    // Prompt and process 1 command at a time
    while (1) {                  // Loop forever
        prompt();                // print prompt
        fgets(line, NL, stdin);  // read a line
        fflush(stdin);           // flush the input buffer

        // Catches EOF (Ctrl-D) and exits when unexpected EOF is encountered
        if (feof(stdin)) {
            fprintf(stderr, "EOF pid %d feof %d ferror %d\n", getpid(), feof(stdin), ferror(stdin));
            exit(0);
        }

        // Catches non-commands and continues to the next prompt
        if (line[0] == '#' || line[0] == '\n' || line[0] == '\000') {
            continue;  // To the next prompt
        }

        // Parsing command line into tokens and checking for background process
        v[0] = strtok(line, sep);
        strcpy(currBgProcess, v[0]);  // Store the current background process
        for (i = 1; i < NV; i++) {
            v[i] = strtok(NULL, sep);  // Get the next token
            if (v[i] == NULL) {        // If no more tokens are found, break out of the loop
                break;
            } else if (*v[i] == '&') {  // If a background process
                ampersand = 1;          // Flag the command
                ampersandCount++;       // Increment background process count
                v[i] = NULL;            // Set the last token to NULL
                break;                  // Break out of the loop
            }

            // Concatenate the current background process with the next token
            strcat(currBgProcess, " ");
            strcat(currBgProcess, v[i]);
        }

        // Check for cd
        if (strcmp(v[0], "cd") == 0) {
            if (chdir(v[1]) == -1) {   // If cd fails
                perror("chdir fail");  // Print error message
            }
            continue;  // Continue to the next prompt if cd succeeds
        }

        // Fork child process to execute v[0]'s command
        switch (frkRtnVal = fork()) {
            // Error in forking child process
            case -1: {
                perror("Fork failed");
                break;
            }
            // Child process
            case 0: {
                if (execvp(v[0], v) == -1) {  // If command execution fails
                    perror("execvp failed");
                    exit(1);
                }
            }
            // Parent process
            default: {
                if (ampersand) {                                          // If there is a background process
                    bgProcesses[ampersandCount] = strdup(currBgProcess);  // Store the background process
                    pids[ampersandCount] = frkRtnVal;                     // Store the PID of the background process
                    printf("[%d] %s done\n", frkRtnVal, currBgProcess);   // Print the PID of the background process
                    fflush(stdout);
                    ampersand = 0;      // Reset ampersand
                } else {                // Wait for child process to terminate
                    wpid = wait(NULL);  // Equivalent to waitpid(-1, NULL, WNOHANG)
                    if (wpid == -1) {
                        perror("waitpid failed");
                    }
                }
                break;
            }
        }  // End of switches
    }  // End of while
}  // End of main