# Configurare Cloudinary per l'upload delle immagini

Questa guida descrive come creare un account Cloudinary gratuito e recuperare
le credenziali necessarie per caricare immagini e ottenere link pubblici da
usare con l'API di Instagram.

## 1. Crea un account Cloudinary

1. Vai su [cloudinary.com](https://cloudinary.com/) e registra un account gratuito.
2. Al termine della registrazione viene creato automaticamente un "cloud"
   (identificato da un **Cloud name**).

## 2. Recupera le credenziali API

1. Apri la [Dashboard di Cloudinary](https://console.cloudinary.com/).
2. Nella sezione **API Keys** trovi:
   - **Cloud name**
   - **API Key**
   - **API Secret** (fai clic su "Reveal" per visualizzarlo)
3. La dashboard mostra anche una variabile pronta all'uso nel formato:

   ```text
   CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>
   ```

## 3. Configura il progetto

Imposta nel file `.env` o la variabile unica `CLOUDINARY_URL`:

```dotenv
CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>
```

oppure le tre variabili separate:

```dotenv
CLOUDINARY_CLOUD_NAME=<cloud_name>
CLOUDINARY_API_KEY=<api_key>
CLOUDINARY_API_SECRET=<api_secret>
```

Puoi opzionalmente impostare `CLOUDINARY_FOLDER` per raggruppare gli upload in
un folder specifico del tuo spazio Cloudinary.

## 4. Proteggi le credenziali

- L'API Secret consente di caricare e gestire file nel tuo account: non
  inserirlo nel repository, non inviarlo in chat o email e non pubblicarlo.
- Conserva `.env` fuori dal controllo versione (è già incluso in `.gitignore`).
- Per CI/CD, memorizza `CLOUDINARY_URL` (o le tre variabili) come secret
  protetto.
- Ruota l'API Secret dalla dashboard se viene esposto.

## Usare l'integrazione del progetto

L'API Python `upload_to_cloudinary` carica un file (restituendo il risultato
come URL HTTPS pubblico) tramite l'SDK ufficiale `cloudinary`:

```python
from instagram_content_creator import upload_to_cloudinary
from instagram_content_creator.api import post_hello_world

uploaded = upload_to_cloudinary("immagine.jpg")
print(uploaded.download_url)

# Il link restituito può essere passato alla pubblicazione Instagram.
media_id = post_hello_world(image_url=uploaded.download_url)
```

Gli upload su Cloudinary sono pubblici per impostazione predefinita tramite
l'URL di delivery restituito (`secure_url`): chiunque conosca il link può
visualizzare il file. Instagram deve poter raggiungere l'URL via HTTPS, il
che è garantito dal dominio `res.cloudinary.com`.
