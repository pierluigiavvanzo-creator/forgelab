# ForgeLab: diagnosi e preparazione Gemini Free Tier

Data: 2026-10-09. Stato: PREPARED, NOT REMOTE TESTED.

## Risultato verificato

Git main: `1d7024f46d03709587913b3e4905d0b324ae7f40`.
Nessuna modifica al codice di produzione, routing, dipendenze o Dental Quote.
Nessuna nuova run Dental, PR, commit, push o merge in questo intervento.
I precedenti test di stabilizzazione restano evidenza valida sul codice invariato;
non dimostrano che un nuovo modello passi il contratto semantico.

Il replay della correzione test esistente con qwen2.5-coder:7b ha dimostrato
una risposta JSON troncata: `done_reason=length`, 2048 token generati,
`AIDeveloperFormatError`. Durata totale 152610 ms, incluso il retry già previsto
dal router dopo il timeout iniziale. Nessuna patch accettata.
Questo prova un limite del budget di output per quella risposta, non prova
che aumentarne il limite risolva la correttezza semantica.

Il replay diagnostico della stessa correzione tramite Aider ha restituito exit 0
in 267140 ms, ma nessuna modifica effettiva. Anche questa alternativa è FAIL.
Non è stata introdotta nel prodotto e non sono stati ripetuti tentativi identici.

## Preparazione concreta

Creato lo script ignorato `.forgelab/runtime/qualify-gemini-free.py`.
Usa soltanto i due file del fixture sintetico inventory, verifica i loro hash,
riusa l'espressione del prompt semantico attuale e i validatori di scope/sintassi
di produzione. Riusa il checker esistente senza modificare le sei verifiche
indipendenti o filtrare i test generati.

Il candidato è `gemini-3.5-flash`, API Interactions, output JSON strutturato.
Il limite diagnostico remoto è 8192 token; nessun budget locale/di produzione
è stato cambiato. Una richiesta per caso, nessun retry automatico,
nessun fallback a servizi a pagamento. I casi 1 e 2 sono separati e nuovi.
Le credenziali sono lette dalla variabile locale `GEMINI_API_KEY`, mai scritte
negli artefatti o inserite nell'URL. Le risposte incomplete vengono rifiutate.

Comando realmente eseguito con Python Aider 3.11:

```powershell
.\.forgelab\tools\aider-0.86.2\Scripts\python.exe .forgelab/runtime/qualify-gemini-free.py --dry-run
```

Esito: exit 0, prompt 9685 caratteri, due percorsi sintetici,
zero chiamate di rete. Questo verifica la preparazione locale, NON il modello,
l'autenticazione, la quota gratuita o il funzionamento dell'API.

## Passaggio necessario del Product Owner

1. Aprire https://aistudio.google.com/ e creare/selezionare un progetto Free Tier.
2. Lasciare la fatturazione disattivata e verificare il piano Free Tier del progetto.
3. Creare una chiave API per quel progetto. Non inviarla in chat.
4. In Windows aprire "Modifica le variabili d'ambiente per l'account" e creare
   la variabile UTENTE `GEMINI_API_KEY`, con la chiave come valore.
5. Comunicare solo: "Progetto Free Tier pronto, fatturazione disattivata,
   GEMINI_API_KEY configurata".

Lo script legge anche la variabile utente dal registro Windows, quindi non è
necessario riavviare Codex. Non eseguire prove finché piano e fatturazione non
sono confermati. Il flag di conferma registra una dichiarazione del proprietario;
non verifica autonomamente il billing Google Cloud.

## Gate successivo

Solo dopo la conferma e la disponibilità della chiave: due prove sintetiche
separate, con test generati e tutte le sei verifiche indipendenti PASS in entrambe.
Un eventuale 2/2 PASS qualifica il candidato su questo fixture: serve ancora
l'integrazione governata e la verifica del percorso completo ForgeLab prima
di raccomandare una run Dental. Il boundary Aider attuale è locale e non viene
aggirato per instradare Gemini.

## Fonti ufficiali consultate

- https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash
- https://ai.google.dev/gemini-api/docs/pricing
- https://ai.google.dev/gemini-api/docs/api-key
- https://ai.google.dev/api/interactions-api

La documentazione indica disponibilità Free Tier e structured output;
accessibilità e quota del progetto reale restano da verificare. Si usa solo il
fixture sintetico anche per evitare l'invio di codice privato o dati reali.
