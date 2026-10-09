# ForgeLab — Laya e MiniCPM: verifica e gate sintetico

Data: 2026-10-09. Esito: nessun backend qualificato.

## Baseline e ambito

Main invariato: `1d7024f46d03709587913b3e4905d0b324ae7f40`.
La richiesta corrente riapre una prova locale circoscritta dopo i due HTTP 503
di Gemini. Nessuna nuova ricerca estesa di modelli. Nessuna modifica a
produzione, routing, dipendenze Python, Dental, Planner, Reviewer o Security.
Nessuna run Dental, promozione, branch, PR, commit, push o merge.

## Laya

Interpretazione esplicita: modello `laya` nel catalogo Ollama.
La documentazione indica un modello decisionale da 421M parametri senza
decoder di linguaggio e senza generazione di testo. Non può restituire file
di codice riparati, quindi è inadatto al ruolo semantic repair.
Richiede inoltre Ollama >=0.40; la versione locale è 0.34.2.
Nessun download o aggiornamento di Ollama effettuato per Laya.
Se l'utente intendeva un altro prodotto omonimo, questa conclusione non vale
per quel prodotto finché non è identificato.

## MiniCPM selezionato

Candidato ufficiale `openbmb/MiniCPM5-2B-GGUF`, quantizzazione Q4_K_M,
licenza Apache-2.0. Import locale: `forgelab-minicpm5-2b-q4`.
File: 1561318368 byte.
SHA256: `ec2d5801640099e97d8d7e8003ad4d81f336e757811f03a26173dddf386602fd`.

Il pull diretto Ollama dal catalogo Hugging Face è fallito con "blocked redirect
to a different host". Seguendo la procedura documentata dal produttore, il GGUF
è stato scaricato tramite hf CLI esistente e importato con Modelfile e template
ChatML espliciti. Non è stata modificata la protezione redirect di Ollama e non
sono stati installati SDK o pacchetti aggiuntivi.

Modelfile: stop `<|im_end|>` e `</s>`, temperature 1.0, top_p 0.95, num_ctx 8192.
Il gate riusa il percorso Aider corrente e i suoi effettivi parametri di richiesta:
i default del Modelfile non implicano che Aider adotti temperature 1.0.
Questa prova non è un benchmark universale di tutte le configurazioni MiniCPM.

## Due prove realmente eseguite

Riutilizzati esattamente fixture inventory protetto, prompt Aider estratto
dall'orchestrator corrente, wrapper di cattura e misuratore memoria precedenti.
Ogni prova usa il workspace temporaneo pulito dell'adapter. Il candidato è
stato scaricato dalla RAM tra le due prove.

| Prova | Durata | Exit adapter | Modifiche | Test generati | Acceptance |
| --- | ---: | ---: | --- | --- | --- |
| 1 | 300016 ms | 124, timeout | Nessuna | NOT RUN | NOT RUN |
| 2 | 300030 ms | 124, timeout | Nessuna | NOT RUN | NOT RUN |

Entrambi i runner diagnostici terminano con exit shell 0 perché serializzano il
risultato dell'adapter: questo NON è PASS. Gli exit dell'adapter sono 124.
Fixture sorgente invariato in entrambe le prove; nessuna patch candidata
disponibile. I checker sono stati preparati ma non eseguiti sul baseline per
evitare un falso PASS. Nessuna risposta completa/usage token da dichiarare.

## Memoria

Campionamento ogni cinque secondi, 60 campioni per prova; non un picco continuo.

| Prova | Minima RAM libera | Massimo campionato working set processi Ollama |
| --- | ---: | ---: |
| 1 | 2.25 GiB | 0.62 GiB |
| 2 | 2.29 GiB | 0.62 GiB |

Questi numeri non sono il consumo totale del sistema né la VRAM del modello.
Il blocco osservato è il timeout senza risultato; non è stata dimostrata una
root cause interna del modello o del runtime. Nessuna dichiarazione di OOM.
Al termine il solo modello del benchmark è stato scaricato dalla RAM;
`ollama ps` ha restituito lista vuota. Le applicazioni aperte sono preservate.
Il candidato resta installato su disco, ma non è attivato nel routing ForgeLab.

## Modifiche locali

Solo file diagnostici ignorati e questo audit:

- `.forgelab/tools/minicpm5-2b/`: GGUF e Modelfile;
- `.forgelab/runtime/run-minicpm5-2b-{1,2}.py`: copie del runner esistente con
  modello/caso aggiornati e rifiuto di sovrascrivere i casi;
- `.forgelab/runtime/check-minicpm5-2b-{1,2}.py`: checker di acceptance invariato
  salvo selezione caso, non eseguito in assenza di candidato;
- `.forgelab/runtime/semantic-completion-audit/qualification-minicpm5-2b-{1,2}/`:
  comandi, prompt, trace, stream parziali, risultati e campioni memoria;
- `.forgelab/runtime/semantic-completion-audit/minicpm5-model-metadata.json`:
  identità, dimensione e hash del peso.

Nessun test di produzione invariato è stato duplicato. Nessun accesso Gemini,
nessuna chiave utilizzata per inferenza e nessuna trasmissione remota di Dental.

## Decisione e singola prossima azione

MiniCPM5 nel percorso corrente: 0/2 PASS, non qualificato.
Laya: incompatibile col ruolo di generazione delle riparazioni.
Non attivare nessuno dei due in produzione e non avviare Dental.

Singola prossima azione: riprendere il gate sintetico Gemini 3.8 quando il
servizio è disponibile, su nuova richiesta esplicita. Nessun retry aggiuntivo
o altra installazione locale è stato avviato.

## Fonti ufficiali

- https://ollama.com/library/laya
- https://huggingface.co/openbmb/MiniCPM5-2B
- https://huggingface.co/openbmb/MiniCPM5-2B-GGUF
- https://github.com/OpenBMB/MiniCPM/blob/main/docs/deployment/ollama.md

Skill usata per il download diretto: hugging-face:hf-cli.
