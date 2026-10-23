# Instagram Content Creator

Piccolo client Python, estendibile, per pubblicare contenuti su un account
Instagram professionale tramite la **Meta Graph API**.

Attualmente supporta:
- **Post immagine** (feed) — incluso un post rapido "Hello World!"
- **Storie** (immagine singola)
- **Caroselli** (2-10 immagini)

L'architettura è pensata per aggiungere facilmente nuovi tipi di contenuto
(es. Reels/video) senza toccare il client HTTP o il flusso di pubblicazione.

## Requisiti

- Python 3.11
- Un account Instagram professionale collegato a una Pagina Facebook
- Le seguenti variabili d'ambiente (vedi `.env.example`):
  - `INSTAGRAM_APP_ID`
  - `INSTAGRAM_USER_ID`
  - `INSTAGRAM_ACCESS_TOKEN`

> Nota: la Graph API non permette post di solo testo. Ogni post/storia
> richiede un'immagine (o video) pubblicamente raggiungibile via HTTPS.

> Nota sull'host: l'host corretto dipende dal tipo di access token.
> I token `IGAA...` (Instagram API with Instagram Login / Business Login)
> richiedono `graph.instagram.com`; i token `EAA...` (Facebook Page token)
> richiedono `graph.facebook.com`. L'host viene rilevato automaticamente dal
> prefisso del token; puoi forzarlo con `INSTAGRAM_API_HOST` nel `.env`.

## Setup

```powershell
# crea e attiva il virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# installa il pacchetto in modalità editable con le dipendenze di sviluppo
pip install -e ".[dev]"

# copia il file di esempio e inserisci le tue credenziali
copy .env.example .env
```

## Utilizzo

### Post immagine (feed)

Da codice:

```python
from instagram_content_creator import post_hello_world

media_id = post_hello_world(image_url="https://example.com/immagine.jpg")
print(f"Pubblicato! Media id: {media_id}")

# oppure con una caption personalizzata
media_id = post_hello_world(
    image_url="https://example.com/immagine.jpg",
    caption="Ciao a tutti!",
)
```

Oppure, in modo equivalente, tramite `publish_content` e `ImagePost`:

```python
from instagram_content_creator.api import publish_content
from instagram_content_creator.content import ImagePost

media_id = publish_content(ImagePost(
    image_url="https://example.com/immagine.jpg",
    caption="Ciao a tutti!",
))
```

Per aggiungere un tag di luogo, passa a `location_id` l'ID del luogo
Facebook Places:

```python
media_id = publish_content(ImagePost(
    image_url="https://example.com/immagine.jpg",
    caption="Ciao da Roma!",
    location_id="ID_DEL_LUOGO_FACEBOOK",
))
```

Da riga di comando:

```powershell
# caption di default ("Hello World!")
python -m instagram_content_creator --image-url "https://example.com/immagine.jpg"

# con caption personalizzata
python -m instagram_content_creator --image-url "https://example.com/immagine.jpg" --caption "Ciao a tutti!"
```

> Il CLI espone solo il post immagine singola. Storie e caroselli vanno
> pubblicati da codice come mostrato sotto.

### Storia (immagine singola)

```python
from instagram_content_creator.api import publish_content
from instagram_content_creator.content import ImageStory

media_id = publish_content(ImageStory(image_url="https://example.com/storia.jpg"))
print(f"Storia pubblicata! Media id: {media_id}")
```

### Carosello (2-10 immagini)

```python
from instagram_content_creator.api import publish_content
from instagram_content_creator.content import CarouselPost

media_id = publish_content(CarouselPost(
    image_urls=[
        "https://example.com/1.jpg",
        "https://example.com/2.jpg",
        "https://example.com/3.jpg",
    ],
    caption="Il mio carosello",
))
print(f"Carosello pubblicato! Media id: {media_id}")
```

### Usare una configurazione esplicita

Per default `publish_content`/`post_hello_world` caricano le credenziali da
variabili d'ambiente (`InstagramConfig.from_env()`). Puoi anche passare una
configurazione esplicita, utile ad esempio per pubblicare su account diversi:

```python
from instagram_content_creator.api import publish_content
from instagram_content_creator.config import InstagramConfig
from instagram_content_creator.content import ImagePost

config = InstagramConfig(
    app_id="...",
    user_id="...",
    access_token="...",
)

media_id = publish_content(
    ImagePost(image_url="https://example.com/immagine.jpg", caption="Ciao!"),
    config=config,
)
```

### Estendere con un nuovo tipo di contenuto

1. Crea una classe in `src/instagram_content_creator/content/` che estenda
   `ContentItem` e implementi `container_params()` (e, se ha più media,
   `child_container_params()`).
2. Pubblicala con `publish_content(TuoNuovoContenuto(...))`: il flusso di
   creazione container + pubblicazione è già gestito da `ContentPublisher`.

## Struttura del progetto

```
src/instagram_content_creator/
  api.py            # funzioni di alto livello (post_hello_world, publish_content)
  client.py         # wrapper HTTP per la Graph API
  config.py         # caricamento delle variabili d'ambiente
  exceptions.py      # InstagramAPIError
  publisher.py      # logica di creazione container + pubblicazione
  content/
    base.py         # ContentItem (classe astratta)
    post.py         # ImagePost
    story.py        # ImageStory
    carousel.py      # CarouselPost
tests/              # test unitari con HTTP mockato (responses)
```

## Test

```powershell
python -m pytest
```

## Configurazione Instagram API Developer

Per far funzionare le chiamate alle API di Instagram dal workflow di GitHub Actions, devi prima creare un'app Meta Developer e collegare un account Instagram Business o Creator.

Per una guida dettagliata e completa, consulta la documentazione dedicata: [Configurazione Instagram API Developer](./docs/instagram-api-developer-configuration.md).

## Esecuzione in GitHub Codespaces

Per avviare il progetto direttamente da un Codespace di GitHub:

1. Apri il repository in GitHub Codespaces.
2. Apri un terminale nel workspace e crea un ambiente virtuale:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

3. Installa le dipendenze del progetto:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

4. Imposta le variabili d'ambiente richieste dall'API di Instagram:

```bash
export INSTAGRAM_APP_ID="<app_id>"
export INSTAGRAM_USER_ID="<user_id>"
export INSTAGRAM_ACCESS_TOKEN="<access_token>"
```

5. Esegui il programma:

```bash
python -m instagram_content_creator --caption "Hello from Codespaces!"
```

Se vuoi usare un'immagine esterna, puoi aggiungere anche il parametro `--image-url`:

```bash
python -m instagram_content_creator --caption "Hello from Codespaces!" --image-url "https://example.com/image.jpg"
```

## Test

Il progetto usa `pytest` come runner dei test. Dalla root del repository puoi eseguire:

```bash
python -m pytest
```

Se preferisci impostare esplicitamente il path del codice sorgente:

```bash
PYTHONPATH=src python -m pytest
```
