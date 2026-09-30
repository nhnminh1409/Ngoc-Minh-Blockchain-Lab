#!/usr/bin/env python3
"""Lab 3.3 — Sign, verify & recover with eth-account.
Run: python lab33.py
"""

from eth_account import Account
from eth_account.messages import encode_defunct

# Generate a random account (NEVER use this key for real funds)
acct = Account.create()
print("address:", acct.address)

# Sign a message
msg = encode_defunct(text="I attended Session 3 / Toi da hoc Buoi 3")
sig = Account.sign_message(msg, acct.key)
print("r:", hex(sig.r))
print("s:", hex(sig.s))
print("v:", sig.v)

# Recover the address from the signature
who = Account.recover_message(msg, signature=sig.signature)
print("recovered:", who)
print("match:", who == acct.address)

# Sign twice to show determinism (RFC 6979)
sig2 = Account.sign_message(msg, acct.key)
print("sig_identical:", sig.signature == sig2.signature)

# Tamper with the message
bad = encode_defunct(text="I attended Session 3 / Toi da hoc Buoi 4")
print("tampered ->", Account.recover_message(bad, signature=sig.signature))