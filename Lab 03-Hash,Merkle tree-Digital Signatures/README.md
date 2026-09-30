# Lab 03 – Hash, Merkle tree & Digital Signatures

Hướng dẫn thực hành và giải thích kết quả khi chạy lại từ đầu.

## Yêu cầu
- Python >= 3.8
- Cài thư viện: `pip install -r requirements.txt` (chỉ cần `eth-account`)

## Các file trong thư mục
- `merkle_starter.py` – Lab 3.2 (Merkle tree)
- `lab33.py` – Lab 3.3 (Sign, verify & recover)
- `answers.md` – Đáp án các câu hỏi Q1–Q4 và kết quả Lab 3.3
- `requirements.txt` – Danh sách thư viện cần cài

---

## Lab 3.1 – Hash properties & toy Proof-of-Work
**Không có file riêng** – code chạy trực tiếp từ đề bài.

**Cách chạy:** Chép đoạn code vào terminal hoặc file `.py`.

**Những gì thay đổi khi chạy lại:**
- Kết quả băm (`sha256`) là **xác định** – cùng đầu vào cho cùng đầu ra.
- PoW: `nonce` và `time` có thể khác nhau mỗi lần chạy (do thời gian xử lý và thứ tự tìm kiếm), nhưng quy luật (cần trung bình 16^k lần thử) là cố định.

**Giải thích:** Mỗi số 0 hex thêm vào nhân khối lượng công việc kỳ vọng lên 16 lần. Việc xác minh chỉ tốn 1 lần băm.

---

## Lab 3.2 – Merkle tree
**File:** `merkle_starter.py`

**Cách chạy:** `python merkle_starter.py`

**Những gì thay đổi khi chạy lại:**
- **Root hash và các proof là xác định** – vì dữ liệu đầu vào (`txs`) và hàm băm (`sha256`) là cố định.
- Các dòng `CHECK` luôn in `OK` nếu cài đặt đúng.
- Thời gian chạy có thể thay đổi chút ít nhưng không ảnh hưởng kết quả.

**Các TODO đã hoàn thành:**
- `merkle_root(leaves)` – dựng cây, nhân đôi node cuối khi tầng lẻ.
- `merkle_proof(leaves, index)` – trả về đường dẫn chứng minh.
- `verify_proof(leaf_hash, proof, root)` – xác minh proof.

---

## Lab 3.3 – Sign, verify & recover with eth-account
**File:** `lab33.py`

**Cách chạy:** `python lab33.py`

**Những gì thay đổi khi chạy lại:**
- **Mọi thứ liên quan đến địa chỉ và chữ ký đều thay đổi** vì `Account.create()` sinh cặp khóa ngẫu nhiên mỗi lần.
- `address`, `r`, `s`, `v`, `recovered`, và `tampered ->` đều khác nhau.
- **Nhưng** `match` luôn là `True` (chữ ký khôi phục đúng địa chỉ) và `sig_identical` luôn là `True` (do RFC 6979 – cùng message và private key cho cùng chữ ký).
- Thông điệp bị sửa (`tampered`) luôn khôi phục ra một địa chỉ khác, chứng minh tính toàn vẹn.

**Giải thích:** ECDSA với RFC 6979 sử dụng nonce được tạo xác định từ private key và message, nên chữ ký giống nhau khi chạy lại cùng một `Account`. Nhưng vì mỗi lần `Account.create()` tạo private key mới, nên toàn bộ kết quả khác biệt.

---

## Tóm tắt thay đổi khi chạy lại toàn bộ lab từ đầu

| Lab | Thành phần | Có thay đổi? | Lý do |
|-----|------------|--------------|-------|
| 3.1 | Hash SHA-256 | Không | Deterministic |
| 3.1 | Nonce, thời gian PoW | Có | Tìm kiếm tuần tự, thời gian phụ thuộc CPU |
| 3.2 | Merkle root, proof | Không | Deterministic |
| 3.3 | Địa chỉ, chữ ký, r,s,v | Có | Private key ngẫu nhiên |
| 3.3 | `match`, `sig_identical` | Không (luôn True) | Deterministic với cùng private key |
| 3.3 | Địa chỉ tampered | Có | Phụ thuộc vào chữ ký gốc |

---

## Lưu ý khi demo cho TA
- Lab 3.2: Chạy `python merkle_starter.py` và chỉ ra cả 4 CHECK đều `OK`.
- Lab 3.3: Chạy `python lab33.py`, chỉ ra `match: True` và `tampered ->` khác địa chỉ gốc, giải thích tính toàn vẹn.
- Bonus MetaMask: không bắt buộc, nhưng nếu làm, địa chỉ khôi phục sẽ trùng với tài khoản MetaMask.

---

## Nộp bài
Đẩy `merkle_starter.py`, `answers.md` lên repo Git của lớp trước 23:59.