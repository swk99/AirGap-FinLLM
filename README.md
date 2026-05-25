# SecureLocalFinLLM

Privacy-preserving, zero-retention LLM system for London Mutual Credit Union internal analysts.
All data stays on-premise. No payload ever leaves the internal VLAN.

---

## File Structure

```
SecureLocalFinLLM/
│
├── src/
│   ├── experiment.py   ← Main runner (PII masking, WAF, session experiments)
│   ├── masker.py       ← PII detection & token substitution
│   ├── inspector.py    ← Prompt-injection rule engine (WAF layer)
│   └── session.py      ← In-RAM session manager with TTL + purge
│
├── data/
│   ├── german_credit.csv       ← UCI German Credit (OpenML #31)
│   └── injection_cases.json    ← Labelled prompt injection test cases
│
└── results/
    ├── pii_masking.json        ← Masking accuracy per PII category
    ├── waf_detection.json      ← Injection detection results (TP/FP/FN)
    └── session_audit.json      ← Session lifecycle events (no payload)
```

---

## Recommended Public Datasets

NeurIPS Datasets & Benchmarks 트랙 기준으로 추천:

| Dataset | Source | Why |
|---|---|---|
| **German Credit** (OpenML #31) | TabZilla, NeurIPS 2023 [4] | 신용 리스크 분류, 1000행, 20 feature. 가장 표준적인 벤치마크 |
| **Home Credit Default Risk** | Kaggle (open) | 대출 상환 예측, 307K행. 실제 대출 포트폴리오와 구조가 유사 |
| **FinBen credit split** | NeurIPS 2024 [1] | 금융 LLM 평가용. risk management 태스크 포함 |

> LMCU 맥락에서는 **German Credit**부터 시작하는 걸 추천. 규모가 작고 feature가 명확해서 PII 마스킹 실험에 바로 붙이기 좋음.

---

## Running

```bash
python src/experiment.py
```

stdlib only — 외부 의존성 없음. 실제 LLM 연결 시:

```bash
ollama pull llama3.1:8b
```

---

## Security Layers

| Layer | Component | What it does |
|---|---|---|
| 1 | NGINX + ModSecurity | WAF: 인젝션 차단, rate-limit, TLS 1.3 only |
| 2 | API Gateway (FastAPI) | RBAC, JWT 30분 만료, MFA via Keycloak |
| 3 | `src/masker.py` | LLM 전달 전 PII 토큰 치환 |
| 4 | LLM (Ollama, local) | 내부 VLAN 격리, 아웃바운드 없음 |
| 5 | Audit logger | 접근 이벤트만 기록, 페이로드 미포함 |

---

## References

**[1]** Xie Q. et al., *"FinBen: A Holistic Financial Benchmark for Large Language Models,"*
NeurIPS 2024 Datasets & Benchmarks Track. https://arxiv.org/abs/2402.12659

**[2]** Zhu F. et al., *"TAT-LLM: A Specialized Language Model for Discrete Reasoning over Tabular and Textual Data,"*
ACM ICAIF 2024, pp. 310–318. https://arxiv.org/abs/2401.13223

**[3]** Li Z. et al., *"Evaluating the Instruction-Following Robustness of Large Language Models to Prompt Injection,"*
EMNLP 2024, pp. 557–568. https://aclanthology.org/2024.emnlp-main.33/

**[4]** McElfresh D. et al., *"When Do Neural Nets Outperform Boosted Trees on Tabular Data?"*
NeurIPS 2023 Datasets & Benchmarks Track. https://arxiv.org/abs/2305.02997
→ German Credit (OpenML #31) is part of the TabZilla benchmark suite.
