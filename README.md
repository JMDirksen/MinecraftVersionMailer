# MinecraftVersionMailer

Python script for sending email when a new Minecraft version has been released

# Docker build & run

```
git clone https://github.com/JMDirksen/MinecraftVersionMailer.git
cd MinecraftVersionMailer
docker build -t minecraftversionmailer .
docker run -dt \
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
