import json
from urllib.request import urlopen, Request
import re
from email.message import EmailMessage
import smtplib
import ssl
import zlib
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d


def main():
    global db
    db = loadDb()
    process_variant_type("java", "release")
    process_variant_type("java", "snapshot")
    process_variant_type("bedrock", "release")
    process_variant_type("bedrock", "preview")
    saveDb(db)


def process_variant_type(variant, type):
    global db
    version = get_latest_version(variant, type)
    if version and version["id"] not in db[variant][type]["versions"]:
        db[variant][type]["versions"] += [version["id"]]
        db[variant][type]["latest"] = version["id"]
        subject = f"New Minecraft {variant.capitalize()} {type} version {
            version["id"]}"
        message = f"Minecraft {variant.capitalize()} {type} version {
            version["id"]} has been released."
        send_mail(subject, message)


def send_mail(subject, message):
    server = db["config"]["mail_server"]
    port = db["config"]["mail_port"]
    context = ssl.create_default_context()
    username = db["config"]["mail_username"]
    password = unobscure(db["config"]["mail_password"])
    from_address = db["config"]["mail_from"]
    to_address = db["config"]["mail_to"]

    msg = EmailMessage()
    msg["From"] = from_address
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.set_content(message)

    with smtplib.SMTP_SSL(server, port, context=context) as smtp:
        smtp.login(username, password)
        smtp.send_message(msg)


def obscure(data: str) -> str:
    return b64e(zlib.compress(data.encode(), 9)).decode()


def unobscure(obscured: str) -> str:
    return zlib.decompress(b64d(obscured.encode())).decode()


def loadDb():
    try:
        with open("db.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        mail_server = input("Mailserver (Like: smtp.gmail.com): ")
        mail_port = input("Mailserver port (Like: 465): ")
        mail_username = input("Mail username (Like: user@gmail.com): ")
        mail_password = obscure(
            input("Mail password (Google App password?): "))
        mail_from = input(
            "Mail from address (Like: Recipient name <recipient@gmail.com>): ")
        mail_to = input("Mail to address (Like: recipient@gmail.com): ")
        with open("db.json", "w") as f:
            db = {
                "config": {
                    "mail_server": mail_server,
                    "mail_port": mail_port,
                    "mail_username": mail_username,
                    "mail_password": mail_password,
                    "mail_from": mail_from,
                    "mail_to": mail_to,
                },
                "java": {
                    "release": {"versions": []},
                    "snapshot": {"versions": []},
                },
                "bedrock": {
                    "release": {"versions": []},
                    "preview": {"versions": []},
                },
            }
            f.write(json.dumps(db))
            return db


def saveDb(db):
    with open("db.json", "w") as f:
        f.write(json.dumps(db))


def get_latest_version(variant, type):
    match variant:
        case "java":
            return get_latest_java_version(type)
        case "bedrock":
            return get_latest_bedrock_version(type)
        case _:
            return False


def get_latest_java_version(type):
    """Get information about the latest version from Mojang."""
    manifest_url = \
        "https://launchermeta.mojang.com/mc/game/version_manifest.json"
    manifest = url_to_obj(manifest_url)
    for latest_version in manifest["versions"]:
        if latest_version["id"] == manifest["latest"][type]:
            break
    version = url_to_obj(latest_version["url"])
    return {
        "id": version["id"],
        "filename": "minecraft_server.%s.jar" % version["id"],
        "download_url": version["downloads"]["server"]["url"],
    }


def get_latest_bedrock_version(type):
    request = Request(
        url="https://www.minecraft.net/en-us/download/server/bedrock",
        data=None,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
    )
    try:
        html = urlopen(request, timeout=5).read().decode('utf-8')
    except TimeoutError:
        print("Timeout!")
        return False
    if type == "preview":
        regex = r"https://www\.minecraft\.net/bedrockdedicatedserver/bin-win-preview/bedrock-server-(.+)\.zip"
    else:
        regex = r"https://www\.minecraft\.net/bedrockdedicatedserver/bin-win/bedrock-server-(.+)\.zip"
    match = re.search(regex, html)
    url = match.group()
    version = match.group(1)
    return {
        "id": version,
        "filename": "bedrock-server-%s.zip" % version,
        "download_url": url,
    }


def url_to_obj(json_url):
    """Download the json and convert it to an object."""
    return json.load(urlopen(json_url))


if __name__ == "__main__":
    main()
