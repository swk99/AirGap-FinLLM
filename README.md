# LMCU Secure On-Premise LLM

Privacy-preserving, zero-retention LLM system for London Mutual Credit Union internal analysts.
All data stays on-premise. No payload ever leaves the internal VLAN.

---

## File Structure

```
lmcu_secure_llm/
│
├── src/
│   ├── experiment.py       ← Main runner (PII masking, WAF, session experiments)
│   ├── masker.py           ← PII detection & token substitution
│   ├── inspector.py        ← Prompt-injection rule engine (WAF layer)
│   ├── session.py          ← In-RAM session manager with TTL + purge
│   └── llm_client.py       ← Ollama wrapper (Llama 3.1 / Mistral 7B)
│
├── data/
│   ├── test_inputs.json    ← Sample member queries for experiments
│   └── injection_cases.json← Labelled prompt injection test cases
│
└── results/
    ├── pii_masking.json    ← Masking accuracy per PII category
    ├── waf_detection.json  ← Injection detection results (TP/FP/FN)
    └── session_audit.log   ← Access event log (no payload content)
```

---

## Security Layers

| Layer | Component | What it does |
|---|---|---|
| 1 | NGINX + ModSecurity | WAF: blocks injections, rate-limits, TLS 1.3 only |
| 2 | API Gateway (FastAPI) | RBAC auth, JWT 30-min expiry, MFA via Keycloak |
| 3 | PII Masker (`src/masker.py`) | Strips PII before LLM sees any text |
| 4 | LLM (Ollama, local) | Runs on isolated VLAN — zero outbound network |
| 5 | Audit logger | Access events only (no payload), append-only storage |

---

## Running the Experiment

```bash
python src/experiment.py
```

No external dependencies — stdlib only.
To run with an actual LLM, install Ollama and pull a model:

```bash
ollama pull llama3.1:8b
```

---

## References

> Only papers from ICAIF, KDD, NeurIPS, EMNLP are cited.

**[1]** Xie Q. et al., *"FinBen: A Holistic Financial Benchmark for Large Language Models,"*
NeurIPS 2024 Datasets & Benchmarks Track.
https://arxiv.org/abs/2402.12659
→ *Motivates the need for secure, task-specific financial LLM evaluation (risk management, RAG, compliance tasks).*

**[2]** Zhu F. et al., *"TAT-LLM: A Specialized Language Model for Discrete Reasoning over Tabular and Textual Data,"*
ACM ICAIF 2024, pp. 310–318.
https://arxiv.org/abs/2401.13223
→ *Shows that using online LLMs (GPT-4) for financial tabular data introduces cost, latency, and data-security risks — motivating local specialised deployment.*

**[3]** Li Z. et al., *"Evaluating the Instruction-Following Robustness of Large Language Models to Prompt Injection,"*
EMNLP 2024, pp. 557–568.
https://aclanthology.org/2024.emnlp-main.33/
→ *Empirically characterises prompt injection vulnerabilities — directly motivates our WAF rule engine design.*
