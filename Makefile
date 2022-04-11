SRC	=	main.py

NAME	=	music-migrator

$(NAME):
	cp $(SRC) $(NAME)
	chmod +x $(NAME)

clean:
	rm -r -f ./__pycache__

all: $(NAME) clean

fclean : clean
	rm -f $(NAME)

re:	fclean	all