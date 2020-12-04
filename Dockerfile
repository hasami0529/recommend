FROM python:3.6

RUN mkdir /Recommender

ENV AUTHLIB_INSECURE_TRANSPORT=1

WORKDIR /Recommender

ADD . /Recommender

RUN pip install -r requirements.txt

RUN pip install --editable /Recommender

CMD gunicorn -b "0.0.0.0:8000" "recommender.app:create_app()"

EXPOSE 8000
