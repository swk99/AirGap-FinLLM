"""
German Credit 실제 데이터는 OpenML #31에서 다운로드:
  https://www.openml.org/d/31
  또는: pip install scikit-learn && python -c "
    from sklearn.datasets import fetch_openml
    d = fetch_openml('credit-g', version=1, as_frame=True)
    d.frame.to_csv('data/german_credit.csv', index=False)
  "

이 스크립트는 동일한 스키마의 소규모 샘플을 생성합니다 (로컬 테스트용).
실제 실험에서는 OpenML #31 원본(1000행)을 사용하세요.
"""
import csv, random, os

random.seed(42)

CHECKING        = ["no checking", "<0", "0<=X<200", ">=200"]
CREDIT_HISTORY  = ["no credits/all paid", "all paid", "existing paid",
                   "delayed previously", "critical/other existing credit"]
PURPOSE         = ["car", "furniture/equipment", "radio/tv", "repairs",
                   "education", "business", "other"]
SAVINGS         = ["no known savings", "<100", "100<=X<500", "500<=X<1000", ">=1000"]
EMPLOYMENT      = ["unemployed", "<1", "1<=X<4", "4<=X<7", ">=7"]
HOUSING         = ["rent", "free", "own"]
JOB             = ["unskilled resident", "unskilled non-resident",
                   "skilled", "high qualif/self emp/mgmt"]

rows = []
for _ in range(200):
    rows.append({
        "checking_status":        random.choice(CHECKING),
        "duration":               random.randint(6, 72),
        "credit_history":         random.choice(CREDIT_HISTORY),
        "purpose":                random.choice(PURPOSE),
        "credit_amount":          random.randint(250, 18424),
        "savings_status":         random.choice(SAVINGS),
        "employment":             random.choice(EMPLOYMENT),
        "installment_commitment": random.randint(1, 4),
        "housing":                random.choice(HOUSING),
        "age":                    random.randint(19, 75),
        "job":                    random.choice(JOB),
        "num_dependents":         random.randint(1, 2),
        "class":                  random.choices(["good", "bad"], weights=[0.7, 0.3])[0],
    })

out = os.path.join(os.path.dirname(__file__), "german_credit.csv")
with open(out, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} rows → {out}")
print("Replace with OpenML #31 original (1000 rows) for real experiments.")
