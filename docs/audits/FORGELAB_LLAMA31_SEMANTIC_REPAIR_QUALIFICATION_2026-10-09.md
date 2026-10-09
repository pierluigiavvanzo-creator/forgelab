# ForgeLab — Llama 3.1 8B: preflight qualificazione

Data: 2026-10-09. Stato finale: LLAMA31_8B_NOT_QUALIFIED, 0/2 PASS.
Il preflight seguente conserva la decisione prima dell'autorizzazione;
gli esiti eseguiti sono registrati nell'aggiornamento finale in fondo.

## Baseline

HEAD locale e main remoto verificati e coincidenti:
`1d7024f46d03709587913b3e4905d0b324ae7f40`.
`git ls-remote origin refs/heads/main` eseguito in sola lettura.
Codice di produzione, routing, dipendenze e Dental invariati.
Nessuna nuova prova MiniCPM, nessun arresto di processi utente.

## Resource preflight eseguito

- RAM fisica: 15.71 GiB; disponibile: 3.30 GiB.
- Memoria virtuale totale riportata da Windows: 26.72 GiB;
  virtuale libera: 4.30 GiB. Non equivale a RAM fisica.
- Pagefile C:\pagefile.sys: allocato 11269 MiB, uso corrente 2038 MiB,
  picco 4141 MiB. Una singola misura non prova paging severo sostenuto.
- Volume modelli rilevato: C:\Users\NITRO\.ollama\models.
  Spazio libero sul volume C: 749.17 GiB.
- Ollama: 0.34.2; due processi Ollama, working set complessivo 48.4 MiB.
- Installati: qwen2.5-coder:7b (4.7 GB) e
  forgelab-minicpm5-2b-q4:latest (1.6 GB).
- Caricati: nessuno, verificato con `ollama ps`.
- GPU: NVIDIA GeForce RTX 4050 Laptop GPU, VRAM totale 6141 MiB,
  libera riportata 5920 MiB (circa 5.78 GiB).
  Il campo used NVIDIA è 0: conservato come dato grezzo, non usato per
  dedurre che tutta la VRAM fisica sia effettivamente disponibile.
- CPU: Intel Core i7-13620H.
- Rilevati processi Python/Node con riferimenti ForgeLab/uvicorn/Next;
  nessuno modificato o arrestato. Il filtro include anche il PowerShell
  del preflight: non equivale a inventario definitivo dei servizi ForgeLab.

Evidenza JSON ignorata:
`.forgelab/runtime/llama31-resource-preflight-2026-10-09.json`.
Nessuna installazione di strumenti diagnostici.

## Model identification

Tag ufficiale candidato: `llama3.1:8b-instruct-q3_K_S`.
Architettura: Llama, 8.03B; quantizzazione Q3_K_S.
Pacchetto pubblicato: 3.7 GB, digest abbreviato `16268e519444`.

Verificato anche `llama3.1:8b-instruct-q3_K_M`: Q3_K_M, 4.0 GB,
digest abbreviato `4faa21fca5a2`. Non selezionato né scaricato.

Fonti ufficiali:
- https://ollama.com/library/llama3.1:8b-instruct-q3_K_S
- https://ollama.com/library/llama3.1:8b-instruct-q3_K_M

La dimensione pubblicata è arrotondata e NON costituisce una stima del consumo
RAM/VRAM del processo. Servono anche KV cache, buffer e runtime.
Non è disponibile una misura locale del footprint di questo modello.

## Decisione risorse e autorizzazione

Una prova isolata con una sola istanza e il contesto del percorso corrente
è ragionevolmente tentabile grazie alla VRAM libera, ma non è garantita.
Rischio operativo atteso: MODERATE. La RAM e la memoria virtuale libera
richiedono osservazione; niente contesto massimo 128K, niente altri modelli
caricati in parallelo, niente arresto di applicazioni utente.

Il candidato non è installato. Il task allegato prescrive:
"If the exact candidate model is NOT already installed: DO NOT DOWNLOAD IT YET."
e "Stop there." Si arresta quindi al preflight:
MODEL_DOWNLOAD_APPROVAL_REQUIRED.

Nessun download, caricamento, benchmark, cambio di routing o PR Llama.
Prova 1 e prova 2: NOT RUN. Qualificazione: NOT RUN.
Il presente documento è l'unico nuovo file audit; il JSON è runtime ignorato.

## Single next action

AUTHORIZE_LLAMA31_8B_DOWNLOAD

Dopo autorizzazione: scaricare soltanto il candidato verificato ed eseguire
il gate sintetico richiesto, senza modificare prompt, formato, budget di repair,
Dental o routing di produzione prima di 2/2 PASS. Il task richiede assenza di
retry dentro le prove: va verificato il comportamento di reflection dell'adapter
prima di riutilizzare i runner precedenti, senza aumentare alcun limite.

## Aggiornamento finale dopo autorizzazione

Il proprietario ha autorizzato esplicitamente `AUTHORIZE_LLAMA31_8B_DOWNLOAD`.
Scaricato esclusivamente il tag ufficiale richiesto. `/api/show` conferma
famiglia llama, 8.0B, GGUF, Q3_K_S. Nessun nuovo pacchetto Python.

Riutilizzati fixture, espressione del prompt semantico, Aider 0.86.2, formato
whole, provider loopback e checker precedenti. Prompt delle due prove identici
byte per byte. Nessuna correzione manuale tra generazione e acceptance.

Solo nel wrapper diagnostico: `Coder.max_reflections=0`, timeout retry Aider
azzerati, `num_retries=0` e guardia che vieta più di una chiamata generativa.
I trace registrano una richiesta e una completion per prova. Non è cambiato
il codice ForgeLab, il prompt, il contesto automatico Aider o il budget repair.

| Prova | Percorsi cambiati | Exit adapter | Durata | Test generati | Acceptance |
| --- | --- | ---: | ---: | --- | --- |
| 1 | inventory_app.py, test_inventory_app.py | 0 | 127405 ms | 8 test, 3 FAIL + 1 ERROR | 6/6 PASS |
| 2 | inventory_app.py, test_inventory_app.py | 0 | 122312 ms | 8 test, 1 FAIL + 2 ERROR | 5/6 PASS, 1 ERROR |

Entrambe senza timeout, fixture protetto invariato, nessuna promozione.
Il checker termina con exit shell 0 anche se un test fallisce: l'esito effettivo
si ricava da `test-summary.json`, non da quell'exit shell.

| Prova | Token input/output | Completion byte | RAM libera prima/minima | Max working set Ollama campionato |
| --- | --- | ---: | --- | ---: |
| 1 | 2459 / 1214 | 4964 | 2.73 / 1.54 GiB | 1.60 GiB |
| 2 | 2459 / 1271 | 5389 | 3.18 / 1.61 GiB | 1.47 GiB |

VRAM rilevata con nvidia-smi durante il campionamento; dati grezzi conservati
nei resource-samples e qualification-summary. Nel primo campione osservato
durante l'esecuzione: 4127 MiB usati e 1794 MiB liberi. Il campionamento
non certifica picchi continui né paging sostenuto.

Classificazione: MODEL_QUALITY. Non dimostrati OOM, instabilità o timeout
attribuibile alle risorse in queste prove.

Prova 1: implementazione supera le sei verifiche indipendenti, ma i test
generati hanno attese matematiche errate e mantengono il test del vecchio
ingresso singolo. Prova 2: oltre ai test falliti, il JSON non espone il campo
subtotal degli elementi, con KeyError sia nei test generati sia nell'acceptance.

La domanda successiva del proprietario sulla possibilità di correggere i test
è pertinente per una fase distinta di repair. Il gate corrente vieta però
"No manual repair": un candidato corretto manualmente non prova il 2/2
autonomo del modello. Inoltre correggere solo i test non risolve il difetto
di implementazione della seconda prova. Nessun test è stato corretto qui.

Limitazione evidence: una riga del trace della seconda prova (linea 8) non è
JSON valido, presumibilmente per scrittura concorrente; il file grezzo è
preservato. Request, completion, usage e risultati sono leggibili e conservati.
Non è stata ripetuta l'inferenza per rigenerare quel log.

Il comando finale per scaricare Llama dalla RAM e acquisire ulteriori metadata
è stato rifiutato nell'interfaccia di autorizzazione e non eseguito. Non viene
dichiarato che il modello sia stato scaricato dalla RAM dopo la seconda prova.

## Delta finale e decisione

Solo audit e strumenti/evidenze runtime ignorati:
prepare-llama31-qualification.py, run/check-llama31-q3ks-{1,2}.py,
summarize-llama31.py, metadata/preflight e cartelle delle due prove.
Nessuna modifica ai file src/tests/dashboard, alle dipendenze o al routing.
Nessuna PR, branch, commit, push, merge o run Dental.
Il modello resta installato su disco. Costi API/provider: EUR 0, inferenza locale.

Risultato: LLAMA31_8B_NOT_QUALIFIED, 0/2 PASS.
Production switch: NONE. PR: NONE.
Next model previsto dal task: MiniCPM4-8B, non scaricato né testato.
Single next action del task: AUTHORIZE_MINICPM4_8B_QUALIFICATION.
Non viene avviato alcun nuovo modello automaticamente.

## Aggiornamento cleanup RAM

Su successiva richiesta esplicita del proprietario, eseguito
`ollama stop llama3.1:8b-instruct-q3_K_S`: exit 0.
Il successivo `ollama ps` mostra lista vuota, quindi nessun modello caricato.
La precedente limitazione del cleanup è risolta. Il modello resta su disco;
nessun altro processo è stato arrestato e l'esito del gate resta 0/2.
