# BB84 Quantum Key Distribution Simulator with AES-256-GCM

## 1. Giới thiệu

**Tên đề tài:** Mô phỏng giao thức phân phối khóa lượng tử BB84 và ứng dụng trong mã hóa dữ liệu AES-256-GCM.

Dự án mô phỏng quá trình Alice và Bob phân phối khóa bằng BB84, mô phỏng tấn công Intercept-Resend của Eve, ước lượng QBER và quyết định tiếp tục hoặc hủy phiên. Khi phiên được chấp nhận, khóa đầu ra được sử dụng trong AES-256-GCM để mã hóa và giải mã dữ liệu.

Dự án có hai nhóm thực nghiệm: khảo sát QBER/tỷ lệ ABORT theo xác suất tấn công Eve và benchmark mã hóa file trên nhiều loại/kích thước dữ liệu.

Đây là mô hình mô phỏng phục vụ học tập, không phải hệ thống QKD vật lý hoặc hệ thống được chứng nhận an toàn.

## 2. Công nghệ

| Công nghệ | Mục đích |
|---|---|
| Python 3.10+ | Ngôn ngữ lập trình |
| Qiskit | Xây dựng mạch lượng tử |
| Qiskit Aer | Mô phỏng phép đo |
| NumPy | Sinh dữ liệu và xử lý mảng |
| PyCryptodome | AES-256-GCM |
| Matplotlib | Trực quan hóa |
| pandas | Phân tích benchmark |
| pytest | Kiểm thử tự động |

## 3. Cấu trúc dự án

```text
CK/
├── attack/
│   └── eve.py
├── bb84/
│   ├── alice.py
│   ├── bob.py
│   ├── key_sifting.py
│   ├── quantum_channel.py
│   └── session.py
├── encryption/
│   ├── aes_gcm.py
│   └── file_encryption.py
├── experiments/
│   ├── results.py
│   ├── scenarios.py
│   ├── file_benchmark.py
│   └── analyze_file_benchmark.py
├── file_transfer/
│   ├── integrity.py
│   └── transfer.py
├── security/
│   ├── key_processing.py
│   └── qber.py
├── tests/
├── visualization/
├── config.py
├── main.py
└── requirements.txt
```

## 4. Quy trình hoạt động

1. Alice sinh bit và cơ sở Z/X, sau đó chuẩn bị qubit bằng mạch Qiskit.
2. Qubit đi qua kênh mô phỏng. Eve có thể thực hiện Intercept-Resend theo xác suất cấu hình.
3. Bob đo qubit bằng cơ sở được chọn độc lập.
4. Alice và Bob sàng lọc các vị trí có cơ sở trùng nhau.
5. Một phần khóa được lấy mẫu để ước lượng QBER. Các bit đã công khai bị loại khỏi phần khóa còn lại.
6. Nếu QBER vượt ngưỡng, phiên ABORT và không tạo khóa AES. Nếu được chấp nhận, chương trình thực hiện bước hậu xử lý khóa minh họa.
7. AES-256-GCM mã hóa dữ liệu. Khi giải mã, thẻ xác thực GCM phải hợp lệ trước khi plaintext được ghi ra file.
8. SHA-256 được tính trên file gốc và file giải mã để kiểm tra dữ liệu khôi phục.

## 5. Cấu hình mô phỏng

Các tham số được đặt trong `config.py`, bao gồm số qubit, seed, bật/tắt Eve, xác suất tấn công, tỷ lệ lấy mẫu QBER và ngưỡng QBER.

Ngưỡng 11% là tham số minh họa của đề tài, không phải ngưỡng bảo mật phổ quát.

## 6. Thực nghiệm QBER và Eve

Chạy:

```powershell
python -m experiments.scenarios --trials 10
```

Có thể tùy chỉnh số lần chạy, số qubit, tỷ lệ lấy mẫu, ngưỡng và thư mục đầu ra:

```powershell
python -m experiments.scenarios --trials 30 --num-bits 4096
python -m experiments.scenarios --trials 10 --sample-rate 0.2 --threshold 0.11
```

Kết quả CSV gồm dữ liệu từng lượt và bảng tổng hợp theo xác suất tấn công. Sinh biểu đồ:

```powershell
python -m visualization.charts
```

## 7. Dataset và benchmark file

Tạo dữ liệu benchmark:

```powershell
python generate_test_data.py
```

Chạy 10 lượt cho mỗi file:

```powershell
python -m experiments.file_benchmark --trials 10 --output results/file_benchmark/repeated/file_benchmark_repeated.csv
```

Phân tích kết quả:

```powershell
python -m experiments.analyze_file_benchmark
```

Bộ dữ liệu hiện có 7 phần mở rộng (.txt, .docx, .png, .jpg, .wav, .mp3, .mp4) và 5 kích thước (1KB, 100KB, 1MB, 10MB, 50MB). Các file phi văn bản do script tạo là dữ liệu nhị phân tổng hợp có chữ ký ban đầu, không bảo đảm là tài liệu/ảnh/âm thanh/video hợp lệ. Vì vậy benchmark đánh giá xử lý byte và hiệu năng mã hóa, không đánh giá khả năng mở/phát nội dung bằng ứng dụng chuyên dụng.

## 8. Chạy chương trình chính

```powershell
python main.py
```

Bật/tắt Eve và thay đổi xác suất tấn công trong `config.py`.

## 9. Kiểm thử

Cài đặt và chạy toàn bộ test:

```powershell
python -m pip install -r requirements.txt
python -m pytest -v
```

Test bao gồm sinh/đo qubit, sàng lọc khóa, Eve, QBER, luồng session, AES-GCM và truyền file. GitHub Actions tự động chạy pytest khi push lên các nhánh được cấu hình hoặc khi tạo pull request.

## 10. Giới hạn và lưu ý bảo mật

- Qubit được mô phỏng bằng Qiskit Aer; không có thiết bị lượng tử vật lý.
- Bit và cơ sở được sinh bằng NumPy PRNG; đây không phải nguồn ngẫu nhiên lượng tử vật lý.
- Kênh lượng tử hiện là kênh lý tưởng, chưa mô phỏng đầy đủ suy hao, nhiễu và lỗi thiết bị.
- Kênh cổ điển chưa có cơ chế xác thực mật mã thực tế.
- QBER được ước lượng trên mẫu hữu hạn nên có sai số thống kê; CONTINUE không chứng minh chắc chắn không có Eve.
- Information Reconciliation hiện là thuật toán sửa lỗi đơn giản phục vụ minh họa, không phải Cascade hoàn chỉnh.
- Toeplitz Privacy Amplification chưa có hạch toán đầy đủ lượng thông tin rò rỉ hoặc phân tích finite-key. Không xem khóa đầu ra là khóa QKD có chứng minh an toàn.
- Mã hóa file hiện đọc toàn bộ file vào RAM; phù hợp quy mô dữ liệu benchmark hiện tại, chưa tối ưu cho file rất lớn.
- SHA-256 trong thí nghiệm dùng để đối chiếu file gốc và file khôi phục; xác thực mật mã của ciphertext do AES-GCM đảm nhiệm.

## 11. Tiến độ

### Đã triển khai

- [x] Mô phỏng Alice, Bob, kênh lượng tử và sàng lọc khóa.
- [x] Mô phỏng Eve Intercept-Resend.
- [x] Ước lượng QBER và quyết định CONTINUE/ABORT.
- [x] Minh họa hậu xử lý khóa và AES-256-GCM.
- [x] Mã hóa/giải mã file và kiểm tra SHA-256.
- [x] Thực nghiệm tự động theo nhiều xác suất tấn công.
- [x] Benchmark file và phân tích thống kê.
- [x] Bổ sung kiểm thử tự động cho các thành phần cốt lõi.

### Hướng phát triển

- [ ] Mô phỏng nhiễu, suy hao và các mô hình tấn công khác.
- [ ] Nghiên cứu xác thực kênh cổ điển.
- [ ] Cải thiện hậu xử lý khóa và phân tích finite-key.
- [ ] Tối ưu mã hóa file theo luồng cho dữ liệu lớn.
- [ ] Mở rộng bộ dữ liệu đa phương tiện hợp lệ và thực nghiệm.
