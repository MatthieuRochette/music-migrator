SRC	=	main.py

NAME	=	music-migrator

install:
	cp $(SRC) $(NAME)
	chmod +x $(NAME)

clean:
	rm -r -f ./__pycache__

all: install clean

fclean : clean
	rm -f $(NAME)

re:	fclean	all