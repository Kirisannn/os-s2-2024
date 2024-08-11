all:	compile run

compile:	even minishell

run:
	./even
	./minishell

even:	even.c
	gcc -Wall -std=c17 -g -o even even.c
	stdbuf -oL ./even 5 > output.log &
	stdbuf -oL ./kill.sh >> output.log

minishell:	minishell.c
	gcc -Wall -std=c17 -g -o minishell minishell.c
	./minishell

clean:
	rm even output.log
	clear