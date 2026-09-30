# ForgeLab MVP-1 — Guida passo passo dalla dashboard

**Data:** 2026-09-26  
**Scopo:** eseguire `FORGELAB_MVP_1_REAL_APPLICATION_TEST` con il minimo intervento manuale del Product Owner.  
**Stato:** guida operativa; non modifica architettura o milestone.

## 1. Avvio locale

Aprire PowerShell:

```powershell
cd "C:\Users\NITRO\source\FORGELAB_M8_1_v0.9.1"
.\Start-ForgeLab.ps1
```

Aprire la dashboard:

`http://127.0.0.1:5173`

API locale:

`http://127.0.0.1:8765`

Il normale test MVP non deve trasformare il Product Owner in debugger o operatore di log.

## 2. Selezionare o registrare l'applicazione target

Dalla dashboard aprire l'area Projects / Applications / Target Project, secondo l'etichetta presente nella UI.

Il target MVP-1 raccomandato è una piccola applicazione esterna a ForgeLab, ad esempio:

**Dental Quote Calculator**

Non usare il repository ForgeLab stesso come applicazione target del test.

## 3. Creare un nuovo Run

Aprire la schermata equivalente a **New Run**.

Verificare che il run punti al repository / branch target corretto.

Non aggiungere feature estranee al test.

## 4. Inserire l'obiettivo

Usare questo obiettivo:

> Add support for three treatments, automatic subtotals, percentage discount and final total. Validate inputs. Modify only necessary files. Add tests. Do not change dependencies or configuration unless necessary and explicitly justified.

Per il primo MVP non aggiungere login, database, PDF, cloud, deploy o nuove dipendenze salvo necessità esplicita e giustificata.

## 5. Premere Run

Da questo punto ForgeLab deve gestire autonomamente il flusso previsto:

`objective -> repository/project context -> Planner -> minimum necessary agents -> isolated implementation -> deterministic tests -> bounded repair if needed -> Reviewer -> Security -> READY_FOR_DECISION`

Il Product Owner non deve chiamare manualmente gli agenti.

## 6. Durante il run

La dashboard deve mostrare stato e outcome ad alto livello.

Elementi attesi:

- piano;
- agenti selezionati;
- modifiche;
- stato test;
- eventuale bounded repair;
- review;
- security;
- rischio;
- decisione finale.

Se un test fallisce, non intervenire immediatamente con PowerShell e non correggere manualmente il codice. ForgeLab deve provare diagnosi e repair entro i limiti configurati.

Se il normale completamento richiede copia di log, stack trace, micro-comandi o retry manuali, registrare il comportamento come failure del gate **G2 — Autonomy**.

## 7. READY_FOR_DECISION

Quando il run raggiunge `READY_FOR_DECISION`, ForgeLab deve fermarsi prima della promozione.

Le decisioni del Product Owner sono:

- `APPROVE`
- `REJECT`
- `REPAIR`

Non approvare prima di avere verificato almeno:

- modifiche richieste;
- test;
- review indipendente;
- security;
- blocker/rischi;
- scope del diff.

## 8. APPROVE

Se il risultato è soddisfacente, scegliere `APPROVE`.

ForgeLab deve promuovere esattamente il risultato revisionato, quindi effettuare il retest previsto e verificare l'equivalenza del diff.

Nessuna promozione deve avvenire prima dell'approvazione esplicita.

## 9. Verifica reale dell'applicazione

Dopo `DONE`, aprire l'applicazione target e verificare il comportamento visibile.

Per il Dental Quote Calculator verificare:

1. tre trattamenti;
2. subtotali automatici;
3. sconto percentuale;
4. totale finale;
5. validazione degli input.

I test verdi da soli non chiudono MVP-1: il comportamento reale deve essere utilizzabile.

## 10. Cinque gate MVP-1

MVP-1 è PASS solo se tutti passano:

1. **G1 — Usability:** il run parte dalla dashboard.
2. **G2 — Autonomy:** niente debugging/log transport/retry orchestration ordinari.
3. **G3 — Real output:** l'app target cambia realmente.
4. **G4 — Quality:** test, review e security passano.
5. **G5 — Human control:** nessuna promozione prima di APPROVE.

## 11. Se il test fallisce

Non aprire una nuova milestone infrastrutturale generale.

Procedura:

1. identificare il singolo product gap bloccante;
2. documentarlo;
3. correggere solo quel gap;
4. rieseguire lo stesso scenario MVP-1.

## 12. Metriche minime da registrare

Per ogni run reale:

- minuti attivi del Product Owner;
- numero di interventi utente;
- tempo a output utilizzabile;
- costo provider/modello;
- cicli automatici di repair;
- tempo sviluppatore manuale evitato;
- difetti scoperti dopo approvazione;
- completamento sì/no senza debugging manuale.

KPI principale:

`USER_TIME_SAVED_PER_SUCCESSFUL_RUN`
