from dotenv import load_dotenv
import os
load_dotenv()
url = os.getenv("DATABASE_URL", "Non définie")
if "://" in url:
    masked_url = url.split("://")[0] + "://***" + url.split("@")[-1] if "@" in url else url
    print(f"URL de la base de données : {masked_url}")
else:
    print(f"URL de la base de données : {url}")
