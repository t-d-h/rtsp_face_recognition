FROM animcogn/face_recognition:cpu-latest

COPY requirements.txt requirements.txt

RUN pip3 install -r ./requirements.txt

COPY app.py app.py

CMD CMD ["flask", "run"]
