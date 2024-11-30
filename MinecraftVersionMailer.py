import json
from urllib.request import urlopen
from urllib.request import Request
import re


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


def loadDb():
    try:
        with open("db.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        with open("db.json", "w") as f:
            db = {
                "java": {"release": {"versions": []}, "snapshot": {"versions": []}},
                "bedrock": {"release": {"versions": []}, "preview": {"versions": []}}
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
