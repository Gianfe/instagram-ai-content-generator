# instagram-ai-content-generator
instagram content generator via github workflows

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
python -m instagram_poster --caption "Hello from Codespaces!"
```

Se vuoi usare un'immagine esterna, puoi aggiungere anche il parametro `--image-url`:

```bash
python -m instagram_poster --caption "Hello from Codespaces!" --image-url "https://example.com/image.jpg"
```

> Se il comando `python -m instagram_poster` non trova il modulo, usa:
>
> ```bash
> PYTHONPATH=src python -m instagram_poster --caption "Hello from Codespaces!"
> ```

## Test

Il progetto usa `pytest` come runner dei test. Dalla root del repository puoi eseguire:

```bash
python -m pytest
```

Se preferisci impostare esplicitamente il path del codice sorgente:

```bash
PYTHONPATH=src python -m pytest
```

In questo repository il file di test esiste già in `tests/`, ma è consigliabile verificare che i test siano effettivamente scoperti da `pytest` e aggiungerne altri se necessario per le funzionalità da validare.
