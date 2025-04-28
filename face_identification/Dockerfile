FROM animcogn/face_recognition:cpu-latest

COPY requirements.txt requirements.txt

RUN pip3 install -r ./requirements.txt

COPY app.py app.py

ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]
