# Lab 04 — Real Bitcoin Blocks: PoW, Fees & Merkle Root
**Full Name:** Nguyễn Hồ Ngọc Minh  
**Student ID:** 11247201  
**Course:** Blockchain  

---

## Execution Summary & Verification Output

The following execution output was verified directly on the Bitcoin mainnet via `bitcoin_explorer_starter.py` for anchor block **#840,000**:

```text
=================================================================
 LAB 04: Real Bitcoin Blocks — Block #840000
 Mode: ONLINE (Blockstream API)
=================================================================

[Block Metadata]
  Hash:        0000000000000000000320283a032748cef8227873ff4872689bf23f1cda83a5
  Bits:        0x17034219
  Merkle Root: 031b417c3a1828ddf3d6527fc210daafcc9218e81f98257f88d4d43bd7a5894f
  Tx Count:    3050
  Timestamp:   1713571767

--- [Task 4.1] Verify Proof-of-Work ---
  Header Raw (80 bytes): 00e05f2aab948491071265ad552351d0...7c411b03b7072366194203177d9863ea
  Computed Hash:         0000000000000000000320283a032748cef8227873ff4872689bf23f1cda83a5
  Decoded Target:        0x0000000000000000000342190000000000000000000000000000000000000000
  Hash Integer Val:      0x0000000000000000000320283a032748cef8227873ff4872689bf23f1cda83a5
  hash_int < target:     True
CHECK 1 (PoW valid: hash < target): OK

--- [Task 4.2] Transaction Anatomy & Fee Rate ---
  Coinbase TXID:            a0db149ace545beabbd87a8d6b20ffd6aa3b5a50e58add49a3d435f898c272cf
  Coinbase Total Outputs:   4,075,061,499 sat (40.75061499 BTC)
  First non-coinbase TXID:  2bb85f4b004be6da54f766c17c1e855187327112c231ef2ff35ebad0ea67c69e
  Transaction Fee:          673,200,000 sat (6.732000 BTC)
  Weight / vsize:           747 WU / 187 vB
  Fee Rate:                 3,600,000.00 sat/vB
CHECK 2 (Tx fee & rate computed correctly): OK

--- [Task 4.3] Recompute Merkle Root ---
  Folding 3050 txids into Merkle tree...
  Computed Merkle Root: 031b417c3a1828ddf3d6527fc210daafcc9218e81f98257f88d4d43bd7a5894f
  Expected Merkle Root: 031b417c3a1828ddf3d6527fc210daafcc9218e81f98257f88d4d43bd7a5894f
CHECK 3 (Merkle root matches block header): OK

=================================================================
 ALL CHECKS PASSED: READY FOR Q1-Q5 ANSWERS!
=================================================================
```

---

## Q1 — Proof-of-Work

### 1. Leading Zero Hex Digits in Target
In anchor block **#840,000**, the block header field `bits` is `0x17034219`.  
The formula decoding Bitcoin's compact 32-bit floating-point format to the 256-bit target integer is:

$$\text{bits} = 0x\text{EEMMMMMM} \implies \text{target} = \text{MMMMMM} \times 256^{(\text{EE} - 3)}$$

Given exponent $\text{EE} = 0x17 = 23$ and mantissa $\text{MMMMMM} = 0x034219$:

$$\text{target} = 0x034219 \times 256^{20} = 0x034219 \times 2^{160}$$

Expressed as a full 256-bit hexadecimal string (64 hex characters):
```text
0x0000000000000000000342190000000000000000000000000000000000000000
```
- This target has exactly **19 leading zero hexadecimal digits** ($19 \times 4 = 76$ zero bits).
- The subsequent hex digit is `3` (binary `0011`), which contributes 2 additional leading zero bits. Thus, the target has a total of **78 leading zero bits**.

### 2. Estimated Work Represented by a Valid Header ($\sim 2^{?}$)
A valid block header must satisfy:

$$\text{dSHA256}(\text{header}) < \text{target}$$

- The total output space of SHA-256 is $2^{256}$.
- Assuming SHA-256 behaves as a uniform random oracle, the probability $P$ of a random header hash falling below the target is:

  $$P = \frac{\text{target}}{2^{256}} = \frac{0x034219 \times 2^{160}}{2^{256}} = \frac{213,529}{2^{96}} \approx \frac{2^{17.7}}{2^{96}} \approx \frac{1}{2^{78.3}}$$

- Therefore, the expected number of hash trials (expected work) required by the entire Bitcoin mining network to find one valid block header is:

  $$\text{Expected Hashes} = \frac{1}{P} \approx 2^{78.3} \approx 3.51 \times 10^{23} \text{ hashes}$$

- Approximating solely by the 19 leading zero hex digits ($16^{19}$) corresponds to at least $2^{76}$ hashes; calculating precisely with the mantissa `0x034219` yields approximately **$\sim 2^{78.3}$ hash trials**.

---

## Q2 — SHA-256 Asymmetry

The profound asymmetry between finding a block (taking the entire global mining network $\sim 10$ minutes at $\sim 10^{20}\text{ H/s}$) and verifying it (taking only 2 hash invocations in under $1\ \mu\text{s}$ on a laptop) stems from two core cryptographic properties of **SHA-256**:

1. **Preimage Resistance (One-Way Function) & Pseudorandomness / Avalanche Effect:**
   - SHA-256 is strictly non-invertible. Altering even a single bit in the header (such as the nonce or timestamp) completely scrambles the output hash in an unpredictable, pseudorandom manner.
   - There is no algebraic formula, shortcut, or optimization to compute the required nonce directly from the target.
   - Consequently, **finding a block (mining)** requires pure brute-force trial and error across sextillions of candidate nonces ($\sim 3.51 \times 10^{23}$ hashes on average at block 840,000).

2. **Deterministic Verification & Constant $O(1)$ Time Complexity:**
   - To **verify**, any full node receiving the 80-byte header only needs to evaluate exactly **two SHA-256 operations**:

     $$\text{hash} = \text{SHA256}(\text{SHA256}(\text{header}))$$

     and compare the resulting 256-bit integer against the decoded `target`.
   - This takes $O(1)$ constant time and negligible computational energy.

This asymmetric property forms the foundation of Proof-of-Work: **"Extremely hard to find, but trivial to verify"** (analogous to verifying solutions in NP complexity classes).

---

## Q3 — Transaction Fees & Fee Spike

### 1. Historical Context at Block #840,000
The block's first non-coinbase transaction (`txs[1]`) paid an astounding fee of **$6.732\text{ BTC}$** ($673,200,000\text{ sat}$) for a transaction of only **$187\text{ vB}$**, yielding an unprecedented fee rate:

$$\text{fee\_rate} = \frac{673,200,000\text{ sat}}{187\text{ vB}} = 3,600,000.00\text{ sat/vB}$$

This occurred on **2024-04-20** due to two concurrent events:
- Block #840,000 marked the **4th Bitcoin Halving**, reducing the block subsidy from 6.25 BTC to 3.125 BTC.
- Simultaneously, the **Runes Protocol** (a new fungible token standard on Bitcoin developed by Casey Rodarmor) activated precisely at block 840,000.
- Speculators, token projects, and collectors aggressively competed to mint the very first Runes (notably Rune 0) and capture the "epic satoshi" of the halving block, triggering an intense fee bidding war in the mempool.

### 2. What This Teaches About How Bitcoin Fees Are Set
- **Block Space Scarcity:** Bitcoin enforces an absolute block capacity constraint (maximum 4,000,000 Weight Units $\approx 1 - 2\text{ MB}$ vsize every 10 minutes).
- **Free Market Priority Auction:** Miners act as rational profit maximizers, sorting transactions from highest to lowest **fee rate ($\text{sat/vB}$)**. When demand surges beyond block supply, users must outbid competitors to secure block space.
- **Value Independence:** Transaction fees do not scale with the amount of Bitcoin transferred (transferring 1,000 BTC vs 0.001 BTC incurs identical costs for the same transaction structure). Fees reflect solely **data footprint ($\text{vsize}$)** and **real-time mempool competition**.

### 3. Comparison with Current Network State (Live Mempool Check)
- **Observation Timestamp:** `2026-09-30 04:18:48 UTC` (`11:18:48 UTC+7`)
- **Source:** Live API from [mempool.space](https://mempool.space/api/v1/fees/recommended)
- **Current Chain Tip:** `969,253`
- **Mempool Pending Transactions:** `76,861 txs` ($\approx 42.85\text{ MB}$)
- **Current Recommended Fee Rates:**
  - High Priority (fastestFee): **$2\text{ sat/vB}$**
  - Medium Priority (halfHourFee): **$1\text{ sat/vB}$**
  - Low Priority (hourFee / minimumFee): **$1\text{ sat/vB}$**

*Observation:* The fee rate during block #840,000 ($3,600,000\text{ sat/vB}$) was **$1,800,000\times$ higher** than today's high-priority fee rate ($2\text{ sat/vB}$), clearly demonstrating the dramatic elasticity of Bitcoin's fee market during peak demand.

---

## Q4 — Coinbase Reward

### 1. Empirical Data Breakdown
According to data verified from Block #840,000:
- **Total Coinbase Outputs (`txs[0]`):**  
  $$\text{Coinbase Total Outputs} = 4,075,061,499\text{ sat} \approx 40.75061499\text{ BTC}$$
- **Statutory Block Subsidy (Post-Halving 4):**  
  $$\text{Subsidy} = 3.125\text{ BTC} = 312,500,000\text{ sat}$$

### 2. Source of the Difference
The difference between total coinbase outputs and the block subsidy is:

$$\Delta = 4,075,061,499\text{ sat} - 312,500,000\text{ sat} = 3,762,561,499\text{ sat} \approx 37.62561499\text{ BTC}$$

This massive discrepancy of **$37.6256\text{ BTC}$** originates entirely from the **aggregated transaction fees** paid by all 3,049 user transactions confirmed in the block:

$$\text{Coinbase Reward} = \text{Block Subsidy} + \sum_{i=1}^{N} \text{Transaction Fee}_i$$

The mining pool **ViaBTC** (who mined block #840,000) collected both the $3.125\text{ BTC}$ newly minted subsidy and the $37.6256\text{ BTC}$ in transaction fees, making total revenue over $40.75\text{ BTC}$. Transaction fees constituted over **92.3%** of the block's total reward, exceeding the block subsidy by more than **12 times**.

---

## Q5 — Merkle Root

The fact that the computed Merkle root matches the block header root exactly proves the complete integrity of the block's entire transaction list, guaranteeing that no transactions were modified, injected, omitted, or reordered. Because double SHA-256 exhibits strong collision resistance and the avalanche effect, altering even a single bit in any of the 3,050 transactions or swapping the positions of any two transactions would produce a completely different root and immediately invalidate the block header.
