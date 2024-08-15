all:	compile even minishell

compile:	even minishell

even:	even.c
	gcc -Wall-g -o even even.c
	stdbuf -oL ./even 5 > output.log &
	stdbuf -oL ./kill.sh >> output.log

minishell:	minishell.c
	gcc -Wall -g -o minishell minishell.c
	./minishell

clean:
	rm even output.log minishell
	clear