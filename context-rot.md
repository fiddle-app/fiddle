### LLM Performance vs. Context Length (Context Rot)

| Token Range | Performance Level | Behavior & Characteristics |
| :--- | :--- | :--- |
| **0 - 8k** | **Optimal (95-100%)** | High reasoning accuracy; instructions followed precisely. |
| **8k - 32k** | **Degrading (70-90%)** | "Lost in the Middle" begins; subtle reasoning errors appear. |
| **32k - 64k** | **Unstable (50-70%)** | Significant instruction drift; difficulty with multi-step logic. |
| **64k - 128k** | **Poor (<50%)** | High hallucination rate; model may ignore earlier context entirely. |
| **128k+** | **Critical Failure** | Massive memory overhead; logic often collapses into repetition. |

---

### The Performance Curve (Conceptual)

```
Performance (%)
 ^
 |  ********** (0-8k: The Sweet Spot)
 |            *
 |             *
 |              * (8k-32k: The Slope)
 |               *
 |                *
 |                 ********** (64k+: The Floor/Rot)
 |__________________________________________> Context Length (Tokens)
```
