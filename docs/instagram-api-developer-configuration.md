# Configurazione Instagram API Developer

Per far funzionare le chiamate alle API di Instagram dal workflow di GitHub Actions, devi prima creare un'app Meta Developer e collegare un account Instagram Business o Creator.

## 1) Registrati a Meta for Developers

1. Apri https://developers.facebook.com/
2. Accedi con il tuo account Facebook Meta (quello che usa il tuo profilo Instagram Business/Creator).
3. Crea una nuova app:
   - vai su "My Apps" > "Create App"
   - scegli il tipo di app adatto (di solito "Business")
   - compila i campi richiesti

## 2) Abilita il prodotto Instagram

Dopo aver creato l'app:

1. Nel menu laterale dell'app, seleziona "Instagram"
2. Attiva il prodotto "Instagram Graph API" o "Instagram Basic Display" in base alle API che vuoi usare
3. Assicurati che l'account Instagram sia collegato come Business o Creator account
4. Collega il profilo Instagram a una Pagina Facebook (se richiesto dal tipo di app)

## 3) Ottieni l'ID dell'account Instagram

L'ID dell'account Instagram è necessario per identificare il profilo con cui vuoi interagire.

Puoi recuperarlo in diversi modi:

- tramite Graph API Explorer
- tramite Meta app settings
- tramite chiamata API

Esempio con Graph API Explorer:

1. Apri https://developers.facebook.com/tools/explorer/
2. Seleziona la tua app
3. Aggiungi il permesso necessario (es. `instagram_basic`, `pages_show_list`, `business_management` o quelli richiesti dal tuo caso d'uso)
4. Esegui una richiesta come:

```bash
me?fields=id,username,account_type
```

Oppure, se vuoi ottenere l'ID dell'account Instagram collegato:

```bash
{ig-user-id}?fields=id,username
```

L'ID ottenuto è il valore da usare come `INSTAGRAM_USER_ID`.

## 4) Genera il token di accesso

Per usare le API di Instagram, serve un access token valido.

Metodo consigliato:

1. Apri il Graph API Explorer di Meta
2. Seleziona la tua app
3. Scegli "Add permission" e abilita i permessi necessari
4. Fai clic su "Generate Access Token"
5. Copia il token generato

Esempio di verifica:

```bash
curl -X GET "https://graph.facebook.com/v19.0/me?fields=id,name&access_token=YOUR_ACCESS_TOKEN"
```

Se il token è valido, la risposta conterrà i dati dell'account collegato.

Nota importante:
- I token di accesso vanno trattati come segreti.
- Non pubblicarli nel codice sorgente o nelle logs.
- Usali solo tramite GitHub Secrets.

## 5) Inserire i valori come secret nel repository GitHub

Nel repository GitHub:

1. Vai su "Settings"
2. Apri "Secrets and variables" > "Actions"
3. Clicca su "New repository secret"
4. Aggiungi almeno questi secret:

- `INSTAGRAM_APP_ID` = ID della tua app Meta
- `INSTAGRAM_USER_ID` = ID dell'account Instagram da usare
- `INSTAGRAM_ACCESS_TOKEN` = token di accesso generato

Esempio di configurazione:

```text
INSTAGRAM_APP_ID = 123456789012345
INSTAGRAM_USER_ID = 17841400000000000
INSTAGRAM_ACCESS_TOKEN = EAAB...token...
```

## 6) Esempio di utilizzo in GitHub Actions

Se il tuo workflow usa le variabili segrete, puoi leggerle così:

```yaml
- name: Call Instagram API
  env:
    INSTAGRAM_APP_ID: ${{ secrets.INSTAGRAM_APP_ID }}
    INSTAGRAM_USER_ID: ${{ secrets.INSTAGRAM_USER_ID }}
    INSTAGRAM_ACCESS_TOKEN: ${{ secrets.INSTAGRAM_ACCESS_TOKEN }}
  run: |
    curl -X GET "https://graph.facebook.com/v19.0/${{ secrets.INSTAGRAM_USER_ID }}?fields=id,username&access_token=${{ secrets.INSTAGRAM_ACCESS_TOKEN }}"
```

## Nota finale

Prima di usare i token in produzione:

- verifica i permessi richiesti
- controlla che l'account Instagram sia un Business/Creator account
- usa sempre secret GitHub e non hardcodare valori sensibili nel repository

Se vuoi, puoi anche aggiungere in questo README un esempio completo di workflow GitHub Actions che usa automaticamente i secret di Instagram.
