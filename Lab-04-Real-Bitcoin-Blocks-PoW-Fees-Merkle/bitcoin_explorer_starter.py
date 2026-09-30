#!/usr/bin/env python3
"""
Lab 04 — Real Bitcoin Blocks: PoW, Fees & Merkle Root
Bitcoin Explorer Starter & Verification Script.

Interacts with the Bitcoin mainnet via Blockstream Esplora REST API (or offline cache).
Verifies:
  - Task 4.1: Real Proof-of-Work (header re-hashing and target decoding)
  - Task 4.2: Transaction fee calculation and fee rate (sat/vB)
  - Task 4.3: Merkle root recomputation from real block transactions
"""

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path
import requests

# Default Anchor Block: #840,000 (4th Bitcoin halving block, 2024-04-20)
DEFAULT_HEIGHT = 840000
API_BASE = "https://blockstream.info/api"
DATA_DIR = Path(__file__).resolve().parent / "data"


def dsha256(b: bytes) -> bytes:
    """Double SHA-256: dSHA256(x) = SHA256(SHA256(x))."""
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()


# ---------------------------------------------------------------------------
# API & Offline Cache Helpers
# ---------------------------------------------------------------------------
def fetch_or_cache(url: str, cache_path: Path, offline: bool = False, is_json: bool = True):
    """Fetch from API or read from local cache if offline or already cached."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if offline:
        if not cache_path.exists():
            raise FileNotFoundError(
                f"[OFFLINE ERROR] Missing required cache file: {cache_path}. "
                "Run once online to populate cache."
            )
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f) if is_json else f.read().strip()

    # Online mode: fetch from API, then save to cache
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        content = resp.json() if is_json else resp.text.strip()
        with open(cache_path, "w", encoding="utf-8") as f:
            if is_json:
                json.dump(content, f, indent=2)
            else:
                f.write(content)
        return content
    except Exception as e:
        if cache_path.exists():
            print(f"[WARNING] API fetch failed ({e}). Falling back to cached data.")
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f) if is_json else f.read().strip()
        raise RuntimeError(f"Failed to fetch {url} and no cache available: {e}")


def load_block_data(height: int, offline: bool = False) -> tuple[dict, str, list[dict], list[str]]:
    """
    Load all required data for a block:
      1. Block details (JSON)
      2. Raw 80-byte header (hex string)
      3. First block transactions (JSON, including coinbase & first non-coinbase)
      4. Complete list of transaction IDs (txids)
    """
    # 1. Block hash from height
    hash_file = DATA_DIR / f"block_{height}_hash.txt"
    block_hash = fetch_or_cache(
        f"{API_BASE}/block-height/{height}",
        hash_file,
        offline=offline,
        is_json=False,
    )

    # 2. Block metadata
    block_file = DATA_DIR / f"block_{height}.json"
    block_info = fetch_or_cache(
        f"{API_BASE}/block/{block_hash}",
        block_file,
        offline=offline,
        is_json=True,
    )

    # 3. Raw 80-byte block header (160 hex characters)
    header_file = DATA_DIR / f"block_{height}_header.hex"
    raw_header_hex = fetch_or_cache(
        f"{API_BASE}/block/{block_hash}/header",
        header_file,
        offline=offline,
        is_json=False,
    )

    # 4. First batch of block transactions (contains coinbase and non-coinbase txs)
    txs_file = DATA_DIR / f"block_{height}_txs.json"
    txs = fetch_or_cache(
        f"{API_BASE}/block/{block_hash}/txs",
        txs_file,
        offline=offline,
        is_json=True,
    )

    # 5. Full list of txids in the block
    txids_file = DATA_DIR / f"block_{height}_txids.json"
    txids = fetch_or_cache(
        f"{API_BASE}/block/{block_hash}/txids",
        txids_file,
        offline=offline,
        is_json=True,
    )

    return block_info, raw_header_hex, txs, txids


# ---------------------------------------------------------------------------
# TODO 1 — REAL BITCOIN PROOF-OF-WORK VERIFICATION
# ---------------------------------------------------------------------------
def decode_bits(bits: int) -> int:
    """
    Decode compact 32-bit format (0xEEMMMMMM) to 256-bit target integer:
      bits = 0xEEMMMMMM
      EE = exponent (bits >> 24)
      MMMMMM = mantissa (bits & 0x00FFFFFF)
      target = MMMMMM * 256^(EE - 3)
    """
    ee = bits >> 24
    mm = bits & 0x00FFFFFF
    return mm * (256 ** (ee - 3))


def verify_pow(raw_header_hex: str, bits: int, expected_block_hash: str) -> tuple[bool, str, int, int]:
    """
    Verify real Proof-of-Work:
      1. Re-hash raw 80-byte block header using double SHA-256 (dsha256).
      2. Display hash in byte-reversed order and check equality with expected block hash.
      3. Compare the numerical hash value (little-endian bytes) with the decoded target.
      Block is valid iff: hash_int < target.
    """
    header_bytes = bytes.fromhex(raw_header_hex)
    assert len(header_bytes) == 80, f"Expected 80-byte header, got {len(header_bytes)}"

    # Double SHA-256 of header
    hash_bytes = dsha256(header_bytes)
    # Bitcoin displays hash reversed (big-endian display for little-endian internal byte array)
    computed_hash_hex = hash_bytes[::-1].hex()

    target = decode_bits(bits)
    # The hash integer to compare against target is little-endian int:
    hash_int = int.from_bytes(hash_bytes, byteorder="little")

    is_valid = (computed_hash_hex == expected_block_hash) and (hash_int < target)
    return is_valid, computed_hash_hex, hash_int, target


# ---------------------------------------------------------------------------
# TODO 2 — TRANSACTION ANATOMY & FEE RATE CALCULATION
# ---------------------------------------------------------------------------
def compute_tx_fee_and_rate(tx: dict) -> tuple[int, int, float]:
    """
    Compute fee and fee rate for a non-coinbase transaction:
      fee = sum(inputs.value) - sum(outputs.value)  [unit: satoshi]
      vsize = ceil(weight / 4)                      [unit: vB]
      fee_rate = fee / vsize                        [unit: sat/vB]
    """
    total_in = sum(vin["prevout"]["value"] for vin in tx["vin"])
    total_out = sum(vout["value"] for vout in tx["vout"])
    fee_sat = total_in - total_out

    weight = tx["weight"]
    vsize = math.ceil(weight / 4)
    fee_rate = fee_sat / vsize

    return fee_sat, vsize, fee_rate


# ---------------------------------------------------------------------------
# TODO 3 — REAL BITCOIN MERKLE ROOT RECOMPUTATION
# ---------------------------------------------------------------------------
def merkle_root(txids: list[str]) -> str:
    """
    Recompute Bitcoin Merkle root from a list of txids.
    Reuses Session 3 bottom-up algorithm with Bitcoin rules:
      1. txids are displayed byte-reversed: convert each with bytes.fromhex(txid)[::-1]
      2. Group adjacent nodes in pairs: dsha256(left + right)
      3. If level count is odd: duplicate the last node (level.append(level[-1]))
      4. Repeat until 1 root node remains.
      5. Convert root back to display order: root[::-1].hex()
    """
    if not txids:
        return ""

    # Convert leaves to internal little-endian byte order
    level = [bytes.fromhex(t)[::-1] for t in txids]

    while len(level) > 1:
        # If odd number of elements, duplicate the last element
        if len(level) % 2 == 1:
            level.append(level[-1])
        # Hash adjacent pairs with double SHA-256
        level = [dsha256(level[i] + level[i + 1]) for i in range(0, len(level), 2)]

    # Final root converted back to display hex format
    return level[0][::-1].hex()


# ---------------------------------------------------------------------------
# Main Execution & Verification Routine
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Lab 04 — Real Bitcoin Blocks Explorer")
    parser.add_argument(
        "--height",
        type=int,
        default=DEFAULT_HEIGHT,
        help=f"Block height to inspect (default: {DEFAULT_HEIGHT})",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Run offline using cached data in data/ directory",
    )
    args = parser.parse_args()

    print("=================================================================")
    print(f" LAB 04: Real Bitcoin Blocks — Block #{args.height}")
    print(f" Mode: {'OFFLINE (cache)' if args.offline else 'ONLINE (Blockstream API)'}")
    print("=================================================================\n")

    # Load block data
    block_info, raw_header_hex, txs, txids = load_block_data(args.height, offline=args.offline)
    block_hash = block_info["id"]
    bits = block_info["bits"]
    expected_merkle = block_info["merkle_root"]
    tx_count = block_info["tx_count"]

    print(f"[Block Metadata]")
    print(f"  Hash:        {block_hash}")
    print(f"  Bits:        {hex(bits)}")
    print(f"  Merkle Root: {expected_merkle}")
    print(f"  Tx Count:    {tx_count}")
    print(f"  Timestamp:   {block_info.get('timestamp')}")
    print()

    # -----------------------------------------------------------------------
    # Task 4.1: PoW Verification
    # -----------------------------------------------------------------------
    print("--- [Task 4.1] Verify Proof-of-Work ---")
    pow_valid, computed_hash, hash_int, target = verify_pow(raw_header_hex, bits, block_hash)
    target_hex = f"{target:064x}"
    hash_hex_val = f"{hash_int:064x}"

    print(f"  Header Raw (80 bytes): {raw_header_hex[:32]}...{raw_header_hex[-32:]}")
    print(f"  Computed Hash:         {computed_hash}")
    print(f"  Decoded Target:        0x{target_hex}")
    print(f"  Hash Integer Val:      0x{hash_hex_val}")
    print(f"  hash_int < target:     {hash_int < target}")

    check1_ok = pow_valid and (computed_hash == block_hash) and (hash_int < target)
    print("CHECK 1 (PoW valid: hash < target):", "OK" if check1_ok else "FAIL")
    print()

    # -----------------------------------------------------------------------
    # Task 4.2: Transaction Anatomy & Fee Rate
    # -----------------------------------------------------------------------
    print("--- [Task 4.2] Transaction Anatomy & Fee Rate ---")
    # txs[0] is coinbase
    coinbase_tx = txs[0]
    coinbase_total_out = sum(out["value"] for out in coinbase_tx["vout"])
    print(f"  Coinbase TXID:            {coinbase_tx['txid']}")
    print(f"  Coinbase Total Outputs:   {coinbase_total_out:,} sat ({coinbase_total_out / 1e8:.8f} BTC)")

    # txs[1] is the first non-coinbase transaction
    tx1 = txs[1]
    fee_sat, vsize, fee_rate = compute_tx_fee_and_rate(tx1)
    print(f"  First non-coinbase TXID:  {tx1['txid']}")
    print(f"  Transaction Fee:          {fee_sat:,} sat ({fee_sat / 1e8:.6f} BTC)")
    print(f"  Weight / vsize:           {tx1['weight']} WU / {vsize} vB")
    print(f"  Fee Rate:                 {fee_rate:,.2f} sat/vB")

    # In anchor block 840000, tx1 paid approx 6.732 BTC fee for 187 vB (~3,600,000 sat/vB)
    check2_ok = fee_sat > 0 and vsize > 0 and fee_rate > 0
    if args.height == DEFAULT_HEIGHT:
        check2_ok = check2_ok and (fee_sat == 673200000) and (vsize == 187) and (round(fee_rate) == 3600000)
    print("CHECK 2 (Tx fee & rate computed correctly):", "OK" if check2_ok else "FAIL")
    print()

    # -----------------------------------------------------------------------
    # Task 4.3: Merkle Root Recomputation
    # -----------------------------------------------------------------------
    print("--- [Task 4.3] Recompute Merkle Root ---")
    print(f"  Folding {len(txids)} txids into Merkle tree...")
    computed_root = merkle_root(txids)
    print(f"  Computed Merkle Root: {computed_root}")
    print(f"  Expected Merkle Root: {expected_merkle}")

    check3_ok = (computed_root == expected_merkle) and (len(txids) == tx_count)
    print("CHECK 3 (Merkle root matches block header):", "OK" if check3_ok else "FAIL")
    print()

    # -----------------------------------------------------------------------
    # Summary Check
    # -----------------------------------------------------------------------
    all_passed = check1_ok and check2_ok and check3_ok
    print("=================================================================")
    if all_passed:
        print(" ALL CHECKS PASSED: READY FOR Q1-Q5 ANSWERS!")
    else:
        print(" SOME CHECKS FAILED! Please inspect errors above.")
    print("=================================================================")
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
