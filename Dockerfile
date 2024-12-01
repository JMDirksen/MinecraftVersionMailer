FROM python:3

WORKDIR /usr/src/app

COPY ./MinecraftVersionMailer.py .

ENV INTERVAL=900
ENV MAIL_SERVER="smtp.gmail.com"
ENV MAIL_PORT=465
ENV MAIL_USER=""
ENV MAIL_PASS=""
ENV MAIL_FROM=""
ENV MAIL_TO=""

CMD [ "python", "./MinecraftVersionMailer.py" ]
