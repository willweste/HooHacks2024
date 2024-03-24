FROM python:3.9

# Install OpenGL libraries, OpenCV, and other dependencies
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev && \
    pip install opencv-python

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=run.py

CMD ["flask", "run", "--host=0.0.0.0"]