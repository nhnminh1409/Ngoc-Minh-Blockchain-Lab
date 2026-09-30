# Lab 03 Answers

## **Lab 3.1: Hash properties & toy Proof of Work**

### **Q1: Each extra leading zero multiplies expected work by ≈ how much? Why?**
* **Multiplier:** Approximately **16 times** (16x).
* **Explanation:** Since SHA-256 outputs hexadecimal characters ($0-9, a-f$), each position in the hex string represents 4 bits ($2^4 = 16$ possible values). Requiring one additional leading zero character reduces the set of valid hashes to $\frac{1}{16}$ of the previous state. Therefore, a miner must try roughly 16 times more nonces on average to find a matching hash.

---

### **Q2: Verifying your found nonce takes how many hash calls? What does this say about PoW?**
* **Number of hash calls:** Exactly **1 hash call**.
* **Implication for PoW:** This highlights the asymmetry of Proof-of-Work: **Finding** a valid nonce is computationally expensive (hard to solve), but **verifying** the nonce is nearly instantaneous and cheap (easy to verify).

---
## **Lab 3.2: Merkle tree**

### **Q3: For $n = 1,000,000$ transactions, how many hashes does one proof contain?**
* **Calculation:** A Merkle proof requires one sibling hash for each level of the tree above the leaves. The height/number of levels is calculated as $\lceil \log_2(n) \rceil$.
* **Result:** $\lceil \log_2(1,000,000) \rceil = \mathbf{20\text{ hashes}}$.

---

### **Q4: Explain one real system that uses exactly this mechanism.**
* **System:** **Bitcoin SPV (Simplified Payment Verification) Nodes / Light Clients**.
* **Explanation:** Light clients do not store the full blockchain data. Instead, they only download block headers containing the Merkle Root. When a light client needs to verify whether a transaction is included in a block, it requests a Merkle Proof from a full node. By hashing the transaction together with the $\log_2(N)$ sibling hashes in the proof, the client can verify inclusion against the known Merkle Root efficiently without downloading all other transactions.

---

## **Lab 3.3: Sign, verify and recover with eth account**

**Task 1: Same message, run twice. Is the signature identical?**

[x] Yes (verified: sig_identical = True)
[ ] No

Which RFC explains this? RFC 6979 defines deterministic generation of the
ECDSA nonce k from the private key and message hash using HMAC, instead of
using a random k each time. This is why signing the same message with the
same key twice produces the same signature (r, s, v). It also removes the
risk of nonce reuse leaking the private key, which is a real vulnerability
when k is random and gets reused.

---
**Task 2: Tampered message**

```
address:    0x16e3A97e0015DAB75B92a9b741Bd7406d11D771c
r:          0x1a05e21c0fc7bd918c2ffd998810a30909d35542e7fb175dd21e03d0426f24a8
s:          0x28c3fb5bf5f74a41376984d4e491c8ae1d859967351687def41106167dfb54c6
v:          27
recovered:  0x16e3A97e0015DAB75B92a9b741Bd7406d11D771c
match:      True
tampered-> 0x26D6Df4F35Bc5824aCc17854EA78BD1076fd1689
```

**Why does this prove integrity?** 

The signature is a function of both the
private key and the exact message bytes, since encode_defunct hashes the
message before signing. Changing even a single character changes the
message hash completely, due to the avalanche effect from Lab 3.1. So
recovering a signer address from the original signature against the
tampered message hash yields a different address than acct.address. Since
the recovered address no longer matches, anyone verifying the signature
can immediately tell the message was altered after it was signed. This is
what gives a digital signature its integrity guarantee, in addition to
authenticity.

**Task 3 (Bonus): MetaMask personal_sign**

[ ] Done, recovered address matched the MetaMask account

[ ] Not attempted

---