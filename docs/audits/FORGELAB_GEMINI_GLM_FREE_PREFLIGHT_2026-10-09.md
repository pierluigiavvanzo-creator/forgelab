# ForgeLab — preflight Gemini 3.8 Flash e GLM-5.3-Flash

Data: 2026-10-09. Esito: verifica documentale completata; nessuna inferenza remota.

## Baseline

Main locale e main remoto verificati: `1d7024f46d03709587913b3e4905d0b324ae7f40`.
Il primo accesso remoto è fallito per DNS nel sandbox; la ripetizione autorizzata
in sola lettura di `git ls-remote origin refs/heads/main` ha verificato lo SHA.
Nessuna modifica tracked a produzione, routing, dipendenze o Dental Quote.
I documenti audit precedenti non tracciati sono stati preservati.

## Richiesta e allegato

La richiesta corrente è valutare il prompt e GLM-5.3-Flash PRIMA di procedere
all'uso Gemini o alla creazione del progetto Free Tier. Non autorizza a saltare
questa verifica e avviare inferenza o configurazione account.

L'allegato propone `gemini-3.8-flash`, esattamente due prove sintetiche,
gate 2/2 PASS, integrazione solo dopo il gate, invio remoto disattivato di default,
opt-in esplicito per sorgenti, nessun Dental, nessun costo e nessun merge.
Questi vincoli sono compatibili con l'approccio; la preparazione precedente
usava invece `gemini-3.5-flash` e non costituisce una qualificazione del 3.8.

Prima del benchmark futuro, il runner deve essere allineato al modello 3.8 e
al provider marker GEMINI_FREE_TIER_DIAGNOSTIC. L'attuale runner diagnostico
verifica schema/sintassi e test in copie temporanee: NON prova ancora il percorso
integrato ToolGateway/Reviewer né l'intera orchestrazione di produzione.
Questa distinzione deve restare esplicita nel gate e nella successiva integrazione.

## Confronto da fonti ufficiali

| Voce | Gemini 3.8 Flash | GLM-5.3-Flash |
| --- | --- | --- |
| Identificativo | gemini-3.8-flash | glm-5.3-flash |
| Disponibilità documentata | Modello stabile | API e Coding Plan |
| Output strutturato | Supported structured outputs | Supporto output JSON documentato; non verificata equivalenza JSON Schema strict |
| API ufficiale gratuita | Standard: input e output Free of charge | Input $0.15 / 1M token; output $0.50 / 1M token |
| Pesi locali necessari usando API | No | No |
| Gate ForgeLab eseguito | No | No |
| Decisione zero-cost | Candidato da verificare con account e quota reali | API ufficiale esclusa per il vincolo zero-cost |

GLM-5.3-Flash ha 320B parametri totali e 18B attivati secondo il produttore:
non è un nuovo piccolo modello da installare sul PC. Il nome Flash e la licenza
dei pesi non rendono gratuita l'inferenza API. Il listino distingue invece
GLM-4.7-Flash e GLM-4.5-Flash come Free: sono modelli diversi e non sono
stati scelti o qualificati in questo intervento.

Annunci di intermediari che offrono GLM-5.3-Flash gratuitamente non provano
un Free Tier ufficiale Z.ai, né quote, identità upstream o condizioni adeguate
a ForgeLab. Nessun intermediario è stato attivato e nessuna gratuità durevole
è stata dedotta da crediti promozionali o dalla chat web gratuita.

## Quote e arresto

Google applica RPM/TPM/RPD per progetto, non per chiave. I limiti effettivi sono
visibili in AI Studio e possono variare: non viene inventata una quota numerica
per il progetto non ancora creato. Disponibilità documentale non prova accesso
API reale o superamento dei test.

GEMINI_API_KEY assente nelle variabili Process e User, verificata soltanto
la presenza, senza stampare valori. Stato: GEMINI_FREE_API_KEY_REQUIRED.
Run sintetica 1: NOT RUN. Run sintetica 2: NOT RUN.
Qualificazione: NOT RUN, 0 successi su 2 richiesti; NON un FAIL sperimentale.
Perciò non è giustificato raccomandare upgrade hardware per un presunto
fallimento Gemini: il backend non è stato ancora provato.

Zero chiamate di inferenza, zero token API consumati, billing non toccato,
nessuna integrazione di produzione, branch, PR, commit o merge.

## Singola prossima azione

Configurare un progetto Gemini Free Tier con billing disattivato e la chiave
in GEMINI_API_KEY locale, senza inviarla in chat. Solo successivamente allineare
il runner ed eseguire il gate sintetico 3.8, senza inviare repository privati.

## Fonti consultate

- https://docs.z.ai/guides/vlm/glm-5.3-flash
- https://docs.z.ai/guides/overview/pricing
- https://docs.z.ai/guides/capabilities/struct-output
- https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash
- https://ai.google.dev/gemini-api/docs/pricing
- https://ai.google.dev/gemini-api/docs/rate-limits

Tutte consultate durante questo preflight. Il solo cambiamento del presente
intervento è questo documento audit; i test invariati non sono stati duplicati.
