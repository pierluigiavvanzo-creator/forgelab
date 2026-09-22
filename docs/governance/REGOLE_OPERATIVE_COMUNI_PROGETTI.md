# REGOLE OPERATIVE COMUNI

Progetti AI / Software - Versione 2026-09-02

## 1. Obiettivo economico

Ogni progetto deve contribuire, direttamente o indirettamente ma in modo misurabile, all'obiettivo strategico di EUR 2.000.000 di patrimonio/valore economico aggiuntivo entro 5 anni.

Il contributo può derivare da:

- ricavi diretti, vendite, SaaS, licenze o bounty;
- rendimento/crescita del capitale, quando pertinente;
- risparmio misurabile di tempo o costi;
- proprietà intellettuale, asset o componenti riutilizzabili;
- validazione commerciale o tecnica che aumenti concretamente la probabilità di creare prodotti monetizzabili.

Ogni milestone sostanziale deve dichiarare il contributo economico atteso. Se non esiste un percorso credibile verso valore economico o strategico, l'attività va abbassata di priorità, congelata o interrotta.

## 2. Metrica guida

### ECONOMIC VALUE x USABLE PRODUCT VALUE / USER TIME

Non ottimizzare quantità di codice, numero di test, numero di milestone o profondità diagnostica come fini a sé stessi.

## 3. Repository-first obbligatorio

Prima di sviluppare una capacità sostanziale custom, verificare repository, librerie, strumenti, API o prodotti maturi già esistenti.

Verificare almeno: licenza/termini, manutenzione, maturità, compatibilità, sicurezza/privacy, costo di integrazione e idoneità commerciale.

Stati di riuso:

### DISCOVERED -> BENCHMARKED -> ADOPTED oppure REJECTED -> INTEGRATED -> USED

Essere elencato come candidato non equivale a essere stato realmente riutilizzato.

## 4. Importanza degli upgrade

Classificare gli interventi significativi:

- A — Product Critical
- B — Material Upgrade
- C — Optimization
- D — Diagnostic / Technical

Il lavoro manuale dell'utente su attività D deve essere eccezionale e giustificato da un rischio A.

## 5. Ruolo dell'utente

L'utente è Product Owner, approvatore e tester finale del prodotto.

Non deve essere normalmente utilizzato come:

- QA ripetitivo;
- trasportatore di log;
- annotatore di dataset;
- debugger;
- esecutore di lunghe sequenze di micro-comandi.

## 6. Pacchetti e autonomia

Preferire il più grande pacchetto sicuro e verificabile rispetto a molti micro-pacchetti.

Gli agenti devono eseguire autonomamente, quando possibile e in modo bounded:

`precheck -> backup/isolation -> implementazione -> test -> diagnostica -> repair -> smoke -> report`

Fermarsi per l'utente ai gate decisionali realmente importanti.

## 7. Diagnostica

La diagnostica deve essere hypothesis-driven e bounded. Non ripetere lo stesso controllo senza nuova evidenza o una nuova ipotesi.

## 8. Prodotto prima dell'infrastruttura

Test verdi e architettura corretta sono necessari ma non dimostrano utilità.

Privilegiare evidenze reali: build utilizzabile, workflow completo, output reale, test con utenti, risultati economici o validazione sul campo.

## 9. Comunicazione

Risposte concise per default. Comunicare principalmente:

### IMPORTANZA -> DECISIONE/RISULTATO -> BLOCCO -> PROSSIMO PASSO

Approfondire quando necessario o richiesto.

## 10. Salute del contesto

Quando log, milestone, branch, versioni o decisioni accumulate rischiano di degradare il contesto, segnalare proattivamente che è opportuno aprire una nuova chat e fornire un handover canonico compatto.

## 11. Definizione generale di progresso

Una modifica è progresso solo se migliora materialmente almeno uno tra:

- contributo economico atteso;
- utilità/qualità del prodotto;
- affidabilità necessaria al prodotto;
- riduzione del lavoro dell'utente;
- conoscenza validata necessaria a una decisione Product Critical.

Queste regole non sostituiscono i vincoli specifici di sicurezza, privacy, autorizzazione, integrità finanziaria o qualità propri di ciascun progetto.
