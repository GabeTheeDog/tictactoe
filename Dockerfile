FROM python:3.9

ADD TicTacToe.py .
ADD Webpage.py .

RUN pip install flask pillow

CMD ["python", "./Webpage.py"]
