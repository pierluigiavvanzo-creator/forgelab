# ForgeLab — Gemini Free semantic repair qualification

## BASELINE

Main locale/remoto verificato nel preflight:
`1d7024f46d03709587913b3e4905d0b324ae7f40`.
Produzione, routing, dipendenze e Dental invariati. Riutilizzata l'evidenza
della ricerca locale; nessuna nuova ricerca di modelli locali.

## FREE-TIER PREFLIGHT

Gemini `gemini-3.8-flash`: disponibilità e output strutturato documentati;
API Standard con input/output Free of charge nel listino ufficiale.
Il proprietario ha confermato progetto Free Tier, fatturazione non collegata
e chiave locale. La chiave è stata letta senza mostrarla o salvarla nei payload.
La risposta non ha segnalato problemi di autenticazione o billing;
l'accessibilità effettiva della generazione resta non dimostrata.
Nessuna verifica autonoma del billing Google Cloud è stata eseguita.

## SYNTHETIC RUN 1

- Caso `qualification-gemini-free-1`.
- HTTP 503, `service_unavailable`: modello sotto domanda elevata.
- Durata 44156 ms; nessuna patch restituita.
- Test generati e acceptance: NOT RUN; token: non comunicati dal provider.
- Fixture sorgente invariato.

## SYNTHETIC RUN 2

- Caso `qualification-gemini-free-2`, richiesta indipendente sullo stesso fixture.
- HTTP 503, `service_unavailable`: modello sotto domanda elevata.
- Durata 65656 ms; nessuna patch restituita.
- Test generati e acceptance: NOT RUN; token: non comunicati dal provider.
- Fixture sorgente invariato.

Esattamente due richieste, nessuna ripetizione automatica della prima.
I payload delle due richieste sono identici. Nessun fallback.

## QUALIFICATION

0/2 PASS: `GEMINI_FREE_BACKEND_NOT_QUALIFIED`.
Blocco effettivo: servizio indisponibile (HTTP 503), non un errore aritmetico,
di schema, di test o un rifiuto esplicito del Free Tier.
Non viene dichiarato alcun PASS semantico o di integrazione.

## PRODUCTION ARCHITECTURE

NONE. Il gate non è passato, quindi nessun provider di produzione,
branch o attivazione di invio remoto di sorgenti privati.
Nessuna run Dental e nessuna promozione automatica.

## CHANGES

Solo runner diagnostico ignorato e questo audit:

- `.forgelab/runtime/qualify-gemini-free.py`: candidato allineato da 3.5 a 3.8,
  marker `GEMINI_FREE_TIER_DIAGNOSTIC`, cattura errori HTTP con redazione della
  chiave e metadata usage quando restituiti.
- Corretto il confronto di integrità del fixture per preservare CRLF:
  `read_bytes().decode()` confronta gli stessi byte/testi letti all'inizio.
  Il precedente `read_text()` normalizzava CRLF producendo un falso negativo.
  Il record della prima prova include una nota esplicita della rettifica;
  nessuna risposta o outcome della richiesta è stato alterato.
- Artefatti runtime: payload sintetici, errori HTTP e risultati delle due prove.

Dry-run allineato a 3.8 realmente eseguito: exit 0, prompt 9685 caratteri,
8192 token massimi configurati, zero chiamate di rete in quel dry-run.
I test di produzione invariati non sono stati ripetuti: non qualificherebbero
un provider che non ha restituito una patch.

## ZERO-COST ENFORCEMENT

Conferma proprietario del billing non collegato, API Standard, chiave in header,
nessuna aggiunta di carte/crediti/billing, nessun servizio alternativo a pagamento,
nessun ciclo di retry. Non viene inventato un consumo token pari a zero:
le risposte 503 non riportano usage.

## PR

NONE. Nessun commit, push o merge in questo intervento.

## RESIDUAL RISK

Il modello non è stato qualificato; due errori 503 non dimostrano che il modello
non sappia risolvere il fixture. Il testo del task suggerisce upgrade hardware
sotto 2/2, ma questa evidenza non giustifica una spesa hardware: un upgrade locale
non risolve l'indisponibilità del servizio remoto. Nessuna ricerca ulteriore
o tentativo extra è stato avviato.

## SINGLE NEXT ACTION

Attendere disponibilità del servizio e richiedere esplicitamente un nuovo gate
sintetico Gemini 3.8, prima di qualsiasi integrazione o nuova run Dental.

## Fonti del preflight

- https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash
- https://ai.google.dev/gemini-api/docs/pricing
- https://ai.google.dev/gemini-api/docs/rate-limits
- https://ai.google.dev/gemini-api/docs/api-key
- https://ai.google.dev/gemini-api/docs/billing

GLM-5.3-Flash resta escluso dal vincolo zero-cost per i prezzi API ufficiali:
https://docs.z.ai/guides/overview/pricing.
