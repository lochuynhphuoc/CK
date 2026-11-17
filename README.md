# BB84 Quantum Key Distribution Simulator with AES-256-GCM

## 1. Giới thiệu

**Tên đề tài:** Mô phỏng giao thức phân phối khóa lượng tử BB84 và ứng dụng trong mã hóa dữ liệu AES-256-GCM.

Dự án mô phỏng giao thức BB84 (Bennett–Brassard 1984) để nghiên cứu quá trình phân phối khóa giữa Alice và Bob, đồng thời đánh giá khả năng phát hiện nghe lén thông qua tỷ lệ lỗi lượng tử QBER (Quantum Bit Error Rate).

Sau khi phiên trao đổi khóa vượt qua bước kiểm tra QBER, chương trình chính tiếp tục mô phỏng xử lý khóa và sử dụng khóa đầu ra cho mã hóa AES-256-GCM. Dự án cũng cung cấp bộ thực nghiệm tự động để khảo sát ảnh hưởng của tỷ lệ tấn công Intercept-Resend của Eve.

Đây là mô hình mô phỏng phục vụ học tập, không phải hệ thống QKD triển khai thực tế hoặc được chứng nhận an toàn.

## 2. Mục tiêu

- Tìm hiểu nguyên lý hoạt động của giao thức BB84.
- Mô phỏng Alice chuẩn bị qubit và Bob đo qubit trên hai cơ sở Z/X.
- Thực hiện sàng lọc khóa dựa trên cơ sở đo.
- Mô phỏng tấn công nghe lén Intercept-Resend của Eve.
- Ước lượng QBER từ một phần khóa sau sàng lọc.
- Quyết định CONTINUE hoặc ABORT dựa trên ngưỡng QBER cấu hình.
- Minh họa xử lý khóa và ứng dụng AES-256-GCM.
- Tự động chạy nhiều mức tấn công, tổng hợp kết quả và trực quan hóa dữ liệu.

## 3. Công nghệ

| Công nghệ | Mục đích |
|---|---|
| Python 3.10+ | Ngôn ngữ lập trình |
| Qiskit | Xây dựng mạch lượng tử |
| Qiskit Aer | Mô phỏng đo qubit |
| NumPy | Sinh dữ liệu ngẫu nhiên |
| PyCryptodome | AES-256-GCM |
| Matplotlib | Vẽ biểu đồ thực nghiệm |

## 4. Cấu trúc dự án

```text
CK/
├── attack/
│   └── eve.py
├── bb84/
│   ├── alice.py
│   ├── bob.py
│   ├── key_sifting.py
│   └── quantum_channel.py
├── encryption/
│   └── aes_gcm.py
├── experiments/
│   ├── results.py
│   └── scenarios.py
├── security/
│   ├── key_processing.py
│   └── qber.py
├── tests/
│   ├── test_aes.py
│   ├── test_bb84.py
│   ├── test_eve.py
│   └── test_qber.py
├── visualization/
│   └── charts.py
├── config.py
├── main.py
├── requirements.txt
└── README.md
```

## 5. Nguyên lý và luồng hoạt động

### 5.1. Chuẩn bị và truyền qubit

Alice tạo chuỗi bit ngẫu nhiên và lựa chọn ngẫu nhiên cơ sở Z hoặc X cho từng bit. Trạng thái qubit được chuẩn bị bằng các cổng lượng tử trên Qiskit.

Kênh lượng tử chuyển các mạch qubit từ Alice đến Bob. Trong mô hình hiện tại, kênh truyền là lý tưởng, chưa mô phỏng suy hao hoặc nhiễu vật lý.

### 5.2. Tấn công Intercept-Resend

Khi được bật, Eve chặn từng qubit theo xác suất tấn công cấu hình, lựa chọn ngẫu nhiên cơ sở Z/X, đo qubit rồi chuẩn bị trạng thái mới gửi đến Bob.

Trong mô hình BB84 lý tưởng, nếu Eve tấn công toàn bộ qubit và chọn cơ sở ngẫu nhiên, QBER kỳ vọng trên khóa đã sàng lọc xấp xỉ 25%. Nếu Eve chỉ tấn công một phần với xác suất (p), QBER kỳ vọng xấp xỉ (0.25p).

### 5.3. Đo và sàng lọc khóa

Bob lựa chọn cơ sở đo độc lập. Alice và Bob giữ lại những vị trí mà hai bên đã sử dụng cùng cơ sở, loại bỏ các vị trí khác. Chuỗi bit còn lại được gọi là khóa sau sàng lọc (sifted key).

### 5.4. Ước lượng QBER

Hai bên công khai một mẫu ngẫu nhiên của khóa sau sàng lọc để đếm số bit sai:

[
QBER = \frac{N_{error}}{N_{sample}} \times 100\%
]

Các bit đã công khai trong mẫu được loại khỏi phần khóa còn lại. Nếu QBER mẫu vượt ngưỡng cấu hình, phiên bị hủy (ABORT); ngược lại, chương trình cho phép tiếp tục (CONTINUE).

Ngưỡng 11% trong cấu hình chỉ là ngưỡng minh họa của đề tài, không phải ngưỡng bảo mật phổ quát. Vì mẫu hữu hạn, QBER đo được có thể dao động quanh giá trị kỳ vọng.

### 5.5. Xử lý khóa và AES-256-GCM

Khi QBER được chấp nhận, chương trình chính minh họa bước Information Reconciliation, Toeplitz Privacy Amplification và sử dụng khóa đầu ra cho AES-256-GCM. Chương trình kiểm tra khả năng giải mã, tính toàn vẹn và phản ứng khi ciphertext bị thay đổi.

Các thuật toán xử lý khóa trong dự án là triển khai phục vụ minh họa; chưa phải một quy trình Cascade/Privacy Amplification hoàn chỉnh có chứng minh an toàn và hạch toán rò rỉ thông tin.

## 6. Thực nghiệm tự động

Module `experiments/scenarios.py` chạy các mức xác suất tấn công Eve từ 0% đến 100%, bước 10%. Mặc định mỗi mức chạy 10 lần với seed khác nhau, tổng cộng 110 lần mô phỏng.

Mỗi lần chạy ghi nhận:

- Xác suất tấn công cấu hình và tỷ lệ qubit thực tế bị Eve chặn.
- Số vị trí trùng cơ sở và độ dài khóa sau sàng lọc.
- Kích thước mẫu, số lỗi và QBER mẫu.
- QBER trên toàn bộ khóa sau sàng lọc để đối chiếu trong mô phỏng.
- Quyết định CONTINUE/ABORT.

Các kết quả được tổng hợp theo từng mức tấn công, gồm QBER mẫu trung bình, độ lệch chuẩn, QBER toàn khóa trung bình và tỷ lệ phiên ABORT.

### 6.1. Chạy thực nghiệm

Tại thư mục gốc dự án:

```powershell
python -m experiments.scenarios
```

Mặc định chương trình chạy 10 lần cho mỗi mức tấn công. Có thể tùy chỉnh:

```powershell
python -m experiments.scenarios --trials 30
python -m experiments.scenarios --trials 10 --num-bits 4096
python -m experiments.scenarios --trials 10 --sample-rate 0.2 --threshold 0.11
```

Các tham số có thể sử dụng:

| Tham số | Mặc định | Ý nghĩa |
|---|---:|---|
| `--trials` | 10 | Số lần chạy ở mỗi mức tấn công |
| `--num-bits` | Giá trị trong `config.py` | Số qubit mỗi lần chạy |
| `--sample-rate` | Giá trị trong `config.py` | Tỷ lệ lấy mẫu QBER |
| `--threshold` | Giá trị trong `config.py` | Ngưỡng QBER |
| `--base-seed` | 10000 | Seed gốc để tái lập thực nghiệm |
| `--output-dir` | `results` | Thư mục lưu CSV |

### 6.2. Dữ liệu đầu ra

Sau khi chạy, thư mục `results/` chứa:

| Tệp | Nội dung |
|---|---|
| `qber_trials.csv` | Dữ liệu chi tiết của từng lần mô phỏng |
| `qber_summary.csv` | Thống kê tổng hợp theo tỷ lệ tấn công |

### 6.3. Kết quả kiểm tra thực nghiệm

Với cấu hình 2048 qubit, tỷ lệ lấy mẫu 20%, ngưỡng QBER 11% và 10 lần chạy cho mỗi mức, lần chạy kiểm tra ghi nhận:

- 0% Eve: cả 10 phiên đều CONTINUE, QBER mẫu bằng 0%.
- 40% Eve: 9/10 phiên CONTINUE và 1/10 phiên ABORT.
- 50% Eve: 8/10 phiên ABORT.
- Từ 60% đến 100% Eve: cả 10 phiên ở mỗi mức đều ABORT.
- 100% Eve: QBER mẫu trung bình xấp xỉ 25.11%, gần giá trị kỳ vọng lý thuyết 25%.

Kết quả trên là một lần chạy thực nghiệm cụ thể. Khi thay đổi seed, số lần chạy, số qubit hoặc tỷ lệ lấy mẫu, các giá trị thống kê có thể thay đổi.

## 7. Trực quan hóa kết quả

Sau khi đã có `results/qber_summary.csv`, chạy:

```powershell
python -m visualization.charts
```

Hai biểu đồ được tạo:

- `results/qber_vs_attack.png`: QBER mẫu trung bình, độ lệch chuẩn, QBER lý thuyết và ngưỡng ABORT.
- `results/abort_rate_vs_attack.png`: tỷ lệ phiên bị hủy theo xác suất tấn công Eve.

Có thể chỉ định đường dẫn đầu vào và thư mục đầu ra:

```powershell
python -m visualization.charts --input results/qber_summary.csv --output-dir results
```

## 8. Chạy chương trình mô phỏng chính

Cấu hình các tham số trong `config.py`, ví dụ:

```python
NUM_BITS = 2048

ENABLE_EVE = False
EVE_ATTACK_PROBABILITY = 1.0

QBER_SAMPLE_RATE = 0.20
QBER_THRESHOLD = 0.11
```

Một số trường hợp:

- Không có Eve: `ENABLE_EVE = False`.
- Eve tấn công 50%: `ENABLE_EVE = True`, `EVE_ATTACK_PROBABILITY = 0.5`.
- Eve tấn công 100%: `ENABLE_EVE = True`, `EVE_ATTACK_PROBABILITY = 1.0`.

Chạy chương trình:

```powershell
python main.py
```

## 9. Cài đặt môi trường

Yêu cầu Python 3.10 trở lên.

Tạo và kích hoạt môi trường ảo trên Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 10. Kiểm thử

Chạy từng bộ kiểm thử:

```powershell
python -m tests.test_bb84
python -m tests.test_eve
python -m tests.test_qber
python -m tests.test_aes
```

## 11. Giới hạn và lưu ý bảo mật

- Đây là mô phỏng phần mềm, không mô phỏng thiết bị lượng tử vật lý.
- Kênh lượng tử chưa mô hình hóa suy hao, nhiễu, lỗi thiết bị hoặc tấn công phần cứng.
- Kênh cổ điển chưa triển khai xác thực mật mã thực tế.
- QBER được ước lượng từ mẫu hữu hạn nên có sai số thống kê; một phiên CONTINUE không chứng minh chắc chắn không có Eve.
- Ngưỡng QBER 11% chỉ là giá trị minh họa.
- Phần sửa lỗi và khuếch đại riêng tư hiện tại chưa phải triển khai đầy đủ có chứng minh bảo mật, chưa hạch toán chặt chẽ lượng thông tin rò rỉ.
- Vì vậy, kết quả mô phỏng không nên được xem là khóa QKD có bảo đảm an toàn để sử dụng trong hệ thống thực tế.

## 12. Tiến độ

### Đã triển khai

- [x] Chuẩn bị, truyền và đo qubit bằng Qiskit.
- [x] Sàng lọc khóa BB84.
- [x] Mô phỏng Eve Intercept-Resend.
- [x] Ước lượng QBER và quyết định CONTINUE/ABORT.
- [x] Minh họa xử lý khóa và AES-256-GCM trong chương trình chính.
- [x] Kiểm tra giải mã và phát hiện ciphertext bị thay đổi.
- [x] Thực nghiệm tự động với 11 mức tấn công.
- [x] Tổng hợp kết quả CSV.
- [x] Trực quan hóa QBER và tỷ lệ ABORT.

### Hướng phát triển

- [ ] Hoàn thiện kiểm thử tự động và kiểm tra biên.
- [ ] Mô phỏng nhiễu và suy hao trên kênh lượng tử.
- [ ] Nghiên cứu xác thực kênh cổ điển.
- [ ] Cải thiện mô hình sửa lỗi, privacy amplification và phân tích finite-key.
- [ ] Thử nghiệm với nhiều số qubit, tỷ lệ lấy mẫu và ngưỡng QBER.

---

**Trạng thái:** Hoàn thành mô hình mô phỏng và bộ thực nghiệm cơ bản; tiếp tục hoàn thiện kiểm thử, đánh giá và báo cáo.
