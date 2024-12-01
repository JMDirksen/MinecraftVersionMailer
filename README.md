# MinecraftVersionMailer

Python script for sending email when a new Minecraft version has been released. With docker container instructions.


## Docker build & run

Before running the container don't forget to fill out the MAIL_ environment variables.
```
git clone https://github.com/JMDirksen/MinecraftVersionMailer.git
cd MinecraftVersionMailer
docker build -t minecraftversionmailer .
docker run -d \
  --name minecraftversionmailer \
  -e INTERVAL=900 \
  -e MAIL_SERVER="smtp.gmail.com" \
  -e MAIL_PORT=465 \
  -e MAIL_USER="" \
  -e MAIL_PASS="" \
  -e MAIL_FROM="" \
  -e MAIL_TO="" \
  --restart unless-stopped \
  minecraftversionmailer
docker ps
docker logs -tf minecraftversionmailer
```


## Docker update

```
cd MinecraftVersionMailer
git pull
docker build -t minecraftversionmailer .
docker rm -f minecraftversionmailer
```
Run with the filled out 'docker run' command above.
