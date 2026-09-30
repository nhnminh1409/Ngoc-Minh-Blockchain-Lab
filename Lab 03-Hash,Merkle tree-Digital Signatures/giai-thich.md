# Giải thích Lab 03 (bản dễ hiểu, tiếng Việt)

File này giải thích lại các câu trả lời một cách đơn giản, kèm chú thích
thuật ngữ. File nộp chính thức vẫn là `answers.md` và `merkle_starter.py`.

---

## Bảng chú thích thuật ngữ

| Thuật ngữ | Giải thích |
|---|---|
| **Hash / băm** | Một hàm biến bất kỳ dữ liệu (văn bản, file...) thành một chuỗi ký tự có độ dài cố định, gọi là "digest". Chỉ cần đổi 1 ký tự trong dữ liệu gốc, kết quả băm ra sẽ khác hoàn toàn. |
| **SHA-256** | Tên một thuật toán băm cụ thể, cho ra kết quả dài 256 bit (32 byte), thường hiển thị dưới dạng 64 ký tự hex. |
| **Hex (thập lục phân)** | Hệ đếm cơ số 16, dùng các ký tự 0-9 và a-f. Mỗi ký tự hex đại diện cho 16 giá trị có thể. |
| **Hiệu ứng tuyết lở (avalanche effect)** | Chỉ cần đổi 1 ký tự nhỏ trong dữ liệu đầu vào, kết quả băm ra sẽ đổi gần như hoàn toàn, không đoán trước được. |
| **Nonce** | Một con số được thêm vào dữ liệu, thử đi thử lại nhiều lần cho đến khi kết quả băm thỏa điều kiện mong muốn (ví dụ: bắt đầu bằng vài số 0). |
| **PoW (Proof of Work)** | "Bằng chứng công việc". Cơ chế yêu cầu máy tính phải tốn nhiều công sức (thử rất nhiều nonce) mới tìm ra một kết quả hợp lệ, nhưng người khác kiểm tra lại chỉ tốn 1 bước rất nhanh. |
| **Merkle tree (cây Merkle)** | Một cấu trúc cây nhị phân, trong đó mỗi nút cha là hash của 2 nút con. Nút trên cùng gọi là "root" (gốc), đại diện tóm tắt cho toàn bộ dữ liệu bên dưới. |
| **Leaf (lá)** | Nút ở tầng thấp nhất của cây Merkle, thường là hash của 1 giao dịch. |
| **Root (gốc)** | Nút trên cùng của cây Merkle, chỉ 1 giá trị hash duy nhất nhưng đại diện cho tất cả các lá bên dưới. |
| **Merkle proof (chứng minh Merkle)** | Một danh sách nhỏ các hash "hàng xóm" (sibling) trên đường đi từ 1 lá lên tới root. Dùng để chứng minh 1 giao dịch có nằm trong cây hay không, mà không cần tải cả cây. |
| **SPV (Simplified Payment Verification)** | Kiểu ví Bitcoin "nhẹ", không tải toàn bộ block, chỉ tải header (chứa Merkle root) và dùng Merkle proof để xác minh giao dịch của mình có nằm trong block hay không. |
| **ECDSA** | Thuật toán chữ ký số dùng đường cong elliptic (Elliptic Curve Digital Signature Algorithm), dùng để ký và xác minh chữ ký trong Bitcoin, Ethereum. |
| **RFC 6979** | Một tài liệu chuẩn kỹ thuật, quy định cách tạo số ngẫu nhiên `k` dùng khi ký ECDSA một cách "tất định" (deterministic), tức luôn ra cùng 1 kết quả nếu ký cùng 1 message bằng cùng 1 khóa. |
| **r, s, v** | Ba thành phần tạo nên 1 chữ ký ECDSA trong Ethereum. `r` và `s` là 2 số dùng để xác minh chữ ký, còn `v` giúp xác định chính xác địa chỉ nào đã ký (vì về mặt toán học có thể có 2 địa chỉ khớp, `v` giúp chọn đúng 1). |
| **Address (địa chỉ ví)** | Một chuỗi ký tự đại diện cho 1 tài khoản trên blockchain, được tính ra từ khóa công khai (public key). |
| **Private key / Public key** | Khóa riêng (giữ bí mật, dùng để ký) và khóa công khai (chia sẻ được, dùng để xác minh chữ ký). Địa chỉ ví được tính ra từ khóa công khai. |
| **encode_defunct** | Một hàm trong thư viện `eth-account`, dùng để đóng gói + băm message trước khi ký, theo đúng chuẩn Ethereum (`personal_sign`). |

---

## Lab 3.1: Hash và PoW đồ chơi

**Câu 1: Tại sao thêm 1 số 0 lại làm tốn công gấp ~16 lần?**

Mỗi ký tự hex có 16 khả năng (0-9, a-f). Muốn kết quả băm bắt đầu bằng
đúng 1 số 0 cụ thể, xác suất là 1/16. Muốn có 2 số 0 liên tiếp, xác suất
là 1/16 × 1/16 = 1/256. Vậy cứ thêm 1 số 0 yêu cầu, số lần thử trung bình
cần thiết lại nhân lên khoảng 16 lần.

**Câu 2: Kiểm tra lại nonce tốn bao nhiêu lần băm?**

Chỉ tốn **1 lần**. Máy kiểm tra chỉ cần băm lại `data + nonce` đúng 1 lần
rồi so xem có đúng số 0 yêu cầu không. Đây chính là điểm hay của PoW: bên
"đào" phải tốn rất nhiều công sức để tìm ra nonce, nhưng bên kiểm tra thì
cực kỳ nhanh, gần như miễn phí. Nhờ vậy toàn mạng có thể tin tưởng nhau mà
không cần tốn quá nhiều tài nguyên để xác minh.

## Lab 3.2: Cây Merkle

**Câu 3: Với 1 triệu giao dịch thì proof có bao nhiêu hash?**

Cây Merkle là cây nhị phân, mỗi tầng số lượng nút giảm đi một nửa. Với
1.000.000 lá thì cần khoảng log2(1.000.000) ≈ 19,93, làm tròn lên là
**20 tầng**. Mỗi tầng chỉ cần 1 hash "hàng xóm" đưa vào proof, nên proof
có đúng **20 hash**, dù dữ liệu gốc lớn tới đâu.

**Câu 4: Ví dụ hệ thống thực tế dùng cơ chế này?**

Ví "nhẹ" **SPV** trong Bitcoin: thay vì tải cả block (có thể rất nặng),
ví chỉ tải phần header nhỏ (chứa root), rồi xin node đầy đủ gửi cho 1
Merkle proof để chứng minh giao dịch của mình nằm trong block đó. Ví tự
tính lại từ dưới lên và so với root đã có trong header, khớp thì tin.

Ví dụ khác: chương trình **airdrop** (chỉ công khai 1 root, ai muốn nhận
quà phải tự gửi proof để chứng minh mình có trong danh sách); hoặc
**proof-of-reserves** (sàn giao dịch công khai root của toàn bộ số dư
khách hàng, mỗi người tự kiểm tra được số dư của mình có nằm trong đó,
mà không thấy được số dư của người khác).

## Lab 3.3: Ký và xác minh chữ ký số

**Nhiệm vụ 1: Ký cùng 1 message 2 lần, chữ ký có giống nhau không?**

Có, **giống nhau hoàn toàn**. Lý do là chuẩn **RFC 6979** quy định cách
tạo số `k` dùng trong lúc ký một cách "tất định" (không ngẫu nhiên thật
sự), tức là cứ đưa cùng 1 khóa riêng và cùng 1 message vào thì luôn ra
đúng 1 kết quả `r, s, v`. Điều này còn giúp tránh 1 lỗi bảo mật nguy hiểm:
nếu dùng `k` ngẫu nhiên mà lỡ trùng nhau giữa 2 lần ký khác nhau, kẻ xấu
có thể tính ngược ra được khóa riêng.

**Nhiệm vụ 2: Sửa 1 ký tự trong message, vì sao địa chỉ khôi phục lại khác?**

Chữ ký được tính dựa trên cả khóa riêng lẫn nội dung chính xác của message
(message được băm trước khi ký). Chỉ cần đổi 1 ký tự, do hiệu ứng tuyết lở
(xem Lab 3.1), kết quả băm của message đã hoàn toàn khác. Khi lấy chữ ký
cũ đem khôi phục địa chỉ dựa trên message mới (đã bị sửa), kết quả tính ra
sẽ là 1 địa chỉ khác, không khớp với địa chỉ ví ban đầu.

Đây chính là bằng chứng cho **tính toàn vẹn (integrity)**: bất kỳ ai xác
minh chữ ký cũng có thể phát hiện ngay message có bị sửa sau khi ký hay
không, chỉ bằng cách so sánh địa chỉ khôi phục được với địa chỉ đã biết
trước đó.

Kết quả thực tế đã chạy:
```
địa chỉ ví ban đầu:        0xa440e67b75f7FbeE0be33ff3E21F7fAC0de2C2e3
địa chỉ khôi phục (đúng):  0xa440e67b75f7FbeE0be33ff3E21F7fAC0de2C2e3  (khớp)
địa chỉ khôi phục (bị sửa): 0xF9B354029c8133D1BdBfE7e59Fb24aafF0b80E2C  (khác hẳn)
```
