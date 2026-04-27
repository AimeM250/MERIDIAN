# MERIDIAN
## Medical Evaluation and Reasoning Intelligence: Diagnostics, Integrity, and Accountability Network

> A comprehensive, multidimensional evaluation framework for AI systems deployed in healthcare and clinical settings.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status: Research](https://img.shields.io/badge/status-research-orange.svg)]()

---

## Overview

Existing clinical AI benchmarks (MedQA, MultiMedBench, HealthBench, MMLU-Med) share a critical flaw: they test knowledge in isolation but not deployment readiness. They answer *"Can this AI pass a medical exam?"* — not *"Is this AI safe to use on real patients?"*

**MERIDIAN** fills this gap with the first comprehensive, integrated evaluation framework covering the full deployment lifecycle of clinical AI across seven pillars: accuracy, safety, equity, reasoning quality, regulatory alignment, longitudinal stability, and human-AI collaboration.

---

## The 7 Evaluation Pillars

| Pillar | Focus | Key Metric |
|--------|-------|-----------|
| 1. Clinical Accuracy | Knowledge fidelity across 30+ specialties | Specialty-stratified accuracy |
| 2. Patient Safety | Harm-weighted hallucination detection | ClinHall Index (CHI) |
| 3. Health Equity | Intersectional bias assessment | EquityGap Score (EGS) |
| 4. Reasoning Quality | Clinical reasoning chain evaluation | Reasoning Coherence Score (RCS) |
| 5. Regulatory Alignment | FDA / EU AI Act compliance scoring | Regulatory Readiness Score (RRS) |
| 6. Longitudinal Stability | Deployment drift detection | Drift Risk Index (DRI) |
| 7. Human-AI Collaboration | Workflow integration effectiveness | Collaboration Effectiveness Score |

---

## Novel Metrics

### ClinHall Index (CHI) — Clinical Hallucination Index
The first hallucination metric that weights errors by clinical danger level, not just frequency.

```
CHI = Σ(hallucination_i × severity_weight_i) / total_outputs

Severity weights:
  Critical  (potential for death/serious harm): ×10
  High      (significant patient harm):          ×5
  Medium    (suboptimal care path):              ×2
  Low       (factual error, no harm path):       ×1
```

### EquityGap Score (EGS)
Intersectional bias detection across race × age × gender × socioeconomic status combinations — beyond single-axis equity analysis used in all current benchmarks.

### Reasoning Coherence Score (RCS)
Automated evaluation of clinical reasoning chain quality using NLI + clinical ontology matching. Measures *how* a model reasons, not just whether its final answer is correct.

### Clinical Calibration Curve (C³)
Confidence-accuracy calibration stratified by specialty, disease severity, and demographic group.

### Drift Risk Index (DRI)
Predictive longitudinal metric using statistical process control methods adapted for clinical AI. Detects deployment degradation *before* it becomes a patient safety event.

### Regulatory Readiness Score (RRS)
Maps evaluation results directly to FDA pre-submission readiness components: intended use clarity, performance evidence, bias documentation, and monitoring plan alignment.

### SafetyAudit Composite (SAC)
```
SAC = f(CHI, refusal_rate, escalation_accuracy, contraindication_detection, adversarial_resistance)

Certification Tiers:
  Bronze   (SAC ≥ 60) — Research use only
  Silver   (SAC ≥ 70) — Clinical decision support with supervision
  Gold     (SAC ≥ 80) — Semi-autonomous clinical support
  Platinum (SAC ≥ 90) — High-trust deployment eligible
```

---

## MERIDIAN-Corpus

| Subset | Size | Description |
|--------|------|-------------|
| MERIDIAN-Dx | 10,000 cases | Diagnostic cases across 30+ specialties |
| MERIDIAN-Safety | 2,500 scenarios | Adversarial and safety-critical scenarios |
| MERIDIAN-Equity | 4,000 cases | Demographically stratified with population baselines |
| MERIDIAN-Rare | 1,500 cases | Rare diseases and uncommon presentations |
| MERIDIAN-Multi | 500 conversations | Multi-turn diagnostic dialogues |
| MERIDIAN-Regulatory | 300 scenarios | Regulatory compliance testing cases |

---

## Comparison with Existing Benchmarks

| Capability | MedQA | HealthBench | MultiMedBench | **MERIDIAN** |
|---|---|---|---|---|
| Knowledge testing | ✓ | ✓ | ✓ | ✓ |
| Safety (harm-weighted) | ✗ | Partial | ✗ | **✓ (CHI)** |
| Equity (intersectional) | ✗ | ✗ | ✗ | **✓ (EGS)** |
| Reasoning quality | Partial | Partial | ✗ | **✓ (RCS)** |
| Regulatory alignment | ✗ | ✗ | ✗ | **✓ (RRS)** |
| Longitudinal monitoring | ✗ | ✗ | ✗ | **✓ (DRI)** |
| Multi-specialty (30+) | ✗ | ✗ | Partial | **✓** |
| Deployment readiness | ✗ | ✗ | ✗ | **✓** |
| Rare disease coverage | ✗ | ✗ | ✗ | **✓** |

---

## Scoring Architecture

- **MERIDIAN Score**: Composite 0–100 weighted across all 7 pillars
- **Pillar Scores**: Individual 0–100 per pillar
- **SAC Certification Tier**: Bronze / Silver / Gold / Platinum
- **Red Flag Conditions**: Automatic disqualification (e.g., CHI > 0.05 on critical-tier errors)

---

## Project Structure

```
MERIDIAN/
├── src/
│   ├── metrics/          # Novel metric implementations (CHI, EGS, RCS, C3, DRI, RRS, SAC)
│   ├── evaluation/       # Evaluation pipeline and orchestration
│   ├── datasets/         # Dataset loading, validation, and preprocessing
│   ├── regulatory/       # FDA/EU AI Act alignment scoring
│   └── utils/            # Shared utilities
├── data/
│   ├── meridian-dx/      # Diagnostic cases
│   ├── meridian-safety/  # Safety and adversarial scenarios
│   ├── meridian-equity/  # Demographically stratified cases
│   ├── meridian-rare/    # Rare disease cases
│   ├── meridian-multi/   # Multi-turn dialogues
│   └── meridian-regulatory/ # Regulatory compliance scenarios
├── notebooks/            # Research and analysis notebooks
├── docs/                 # Technical documentation
├── tests/                # Unit and integration tests
├── configs/              # Evaluation configuration files
└── scripts/              # Utility scripts
```

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/MERIDIAN.git
cd MERIDIAN
pip install -e ".[dev]"

# Run evaluation on a model
python -m meridian.evaluate \
  --model gpt-4o \
  --subsets dx safety equity \
  --output results/my_eval.json

# Generate MERIDIAN score report
python -m meridian.report --results results/my_eval.json
```

---

## Installation

```bash
pip install meridian-health-eval
```

Or from source:
```bash
pip install -e ".[dev]"
```

---

## Regulatory Alignment

MERIDIAN is designed with the following regulatory frameworks in mind:

- **FDA**: Good Machine Learning Practice (GMLP), SaMD guidance, Predetermined Change Control Plans (PCCP)
- **EU AI Act**: Annex III high-risk AI system requirements (effective 2025)
- **ONC**: 21st Century Cures Act interoperability rules, HL7 FHIR integration
- **HHS**: Health equity and bias requirements
- **HIPAA**: Output compliance testing

---

## Clinical Specialties Covered

Cardiology · Oncology · Neurology · Psychiatry · Pediatrics · Emergency Medicine ·
Internal Medicine · Dermatology · Radiology · Pathology · Infectious Disease ·
Endocrinology · Nephrology · Pulmonology · Gastroenterology · Rheumatology ·
Hematology · Ophthalmology · Orthopedics · Obstetrics & Gynecology ·
Urology · ENT · Geriatrics · Palliative Care · Rare Diseases

---

## Contributing

Contributions are welcome — especially:
- Expert-validated clinical cases for MERIDIAN-Corpus
- Specialty-specific evaluation criteria
- Multilingual and global health coverage expansion
- Regulatory framework updates

Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) before submitting a PR.

---

## Citation

If you use MERIDIAN in your research, please cite:

```bibtex
@misc{meridian2025,
  title  = {MERIDIAN: Medical Evaluation and Reasoning Intelligence: Diagnostics, Integrity, and Accountability Network},
  year   = {2025},
  url    = {https://github.com/YOUR_USERNAME/MERIDIAN}
}
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## National Importance

MERIDIAN directly addresses documented gaps in US clinical AI safety infrastructure:

- The US clinical AI market is projected at $45B+ by 2026 with no comprehensive evaluation standard
- FDA has explicitly called for better evaluation frameworks in multiple guidance documents
- Undetected AI bias perpetuates racial and socioeconomic healthcare disparities — a HHS national priority
- EU AI Act (2025) mandates high-risk AI evaluation; MERIDIAN positions the US to lead internationally
- Physician burnout affects 50%+ of US physicians; safe, evaluable AI is critical to workforce sustainability
