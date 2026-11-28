# MÔ PHỎNG GIAO THỨC PHÂN PHỐI KHÓA LƯỢNG TỬ BB84 KẾT HỢP MÃ HÓA AES-256-GCM

## 1. Giới thiệu đề tài

**Tên đề tài:** Mô phỏng giao thức phân phối khóa lượng tử BB84 và ứng dụng trong mã hóa dữ liệu AES-256-GCM.

Dự án xây dựng một hệ thống mô phỏng quá trình phân phối khóa lượng tử theo giao thức BB84 giữa Alice và Bob, đồng thời mô phỏng hành vi nghe lén của Eve bằng phương pháp Intercept-Resend.

Sau quá trình truyền và đo qubit, Alice và Bob thực hiện sàng lọc khóa, ước lượng tỷ lệ lỗi bit lượng tử (Quantum Bit Error Rate – QBER) và quyết định tiếp tục hoặc hủy phiên phân phối khóa.

Nếu phiên được chấp nhận, khóa được xử lý qua các bước hậu xử lý minh họa và sử dụng làm đầu vào cho thuật toán mã hóa AES-256-GCM. Hệ thống hỗ trợ mã hóa, giải mã tệp tin và kiểm tra tính toàn vẹn dữ liệu sau khi khôi phục.

Đề tài tập trung vào ba nội dung chính:

- Mô phỏng giao thức phân phối khóa lượng tử BB84 và cơ chế phát hiện nghe lén.
- Tích hợp khóa được tạo từ BB84 với thuật toán mã hóa đối xứng AES-256-GCM.
- Thực nghiệm, kiểm thử và đánh giá QBER, tỷ lệ hủy phiên, tính toàn vẹn và hiệu năng xử lý tệp tin.

**Lưu ý:** Đây là hệ thống mô phỏng phục vụ mục đích học tập và nghiên cứu. Dự án không sử dụng thiết bị lượng tử vật lý và không phải hệ thống QKD được chứng nhận an toàn.

## 2. Công nghệ và thư viện sử dụng

| Công nghệ / Thư viện | Mục đích sử dụng                                              |
| ------------------------ | ------------------------------------------------------------------ |
| Python 3.10+             | Ngôn ngữ lập trình chính                                      |
| Qiskit                   | Xây dựng và biểu diễn mạch lượng tử                       |
| Qiskit Aer               | Mô phỏng hoạt động của mạch lượng tử và phép đo qubit |
| NumPy                    | Sinh dữ liệu, xử lý mảng và tính toán                      |
| PyCryptodome             | Triển khai thuật toán AES-256-GCM                               |
| Matplotlib               | Xây dựng biểu đồ trực quan hóa kết quả                    |
| pandas                   | Đọc, xử lý và phân tích dữ liệu thực nghiệm             |
| pytest                   | Kiểm thử tự động các thành phần của hệ thống            |

Các phiên bản thư viện được quản lý trong tệp `requirements.txt`.

## 3. Yêu cầu môi trường

Để cài đặt và chạy dự án, cần chuẩn bị:

- Hệ điều hành Windows, Linux hoặc macOS.
- Python phiên bản 3.10 trở lên.
- Git (khuyến nghị).
- Visual Studio Code hoặc một trình soạn thảo Python tương đương.
- Kết nối Internet trong quá trình cài đặt các thư viện.

## 4. Cài đặt và khởi chạy dự án

### 4.1. Tải mã nguồn

Clone repository:

```powershell
git clone https://github.com/lochuynhphuoc/CK.git
cd CK
```

Nếu repository ở chế độ private, cần có quyền truy cập GitHub tương ứng.

### 4.2. Tạo môi trường ảo Python

Trên Windows PowerShell:

```powershell
python -m venv .venv
```

Kích hoạt môi trường ảo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Nếu PowerShell không cho phép chạy script kích hoạt, có thể sử dụng Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

### 4.3. Cài đặt thư viện

Sau khi kích hoạt môi trường ảo:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Kiểm tra các thư viện:

```powershell
python -m pip check
```

### 4.4. Chạy chương trình chính

```powershell
python main.py
```

Chương trình thực hiện mô phỏng phiên BB84, xử lý khóa và tích hợp với quá trình mã hóa, giải mã dữ liệu theo cấu hình trong `config.py`.

## 5. Cấu trúc thư mục dự án

```text
CK/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── attack/
│   └── eve.py
│
├── bb84/
│   ├── alice.py
│   ├── bob.py
│   ├── key_sifting.py
│   ├── quantum_channel.py
│   └── session.py
│
├── data/
│   └── benchmark/
│       ├── docx/
│       ├── jpg/
│       ├── mp3/
│       ├── mp4/
│       ├── png/
│       ├── txt/
│       ├── wav/
│       └── manifest
│
├── encryption/
│   ├── aes_gcm.py
│   └── file_encryption.py
│
├── experiments/
│   ├── results.py
│   ├── scenarios.py
│   ├── file_benchmark.py
│   └── analyze_file_benchmark.py
│
├── file_transfer/
│   ├── integrity.py
│   └── transfer.py
│
├── security/
│   ├── key_processing.py
│   └── qber.py
│
├── tests/
│
├── visualization/
│   └── charts.py
│
├── config.py
├── generate_test_data.py
├── main.py
├── requirements.txt
└── README.md
```

**Chức năng các thành phần chính:**

| Thư mục / Tệp          | Chức năng                                         |
| ------------------------- | --------------------------------------------------- |
| `attack/`               | Mô phỏng hành vi nghe lén của Eve              |
| `bb84/`                 | Triển khai các thành phần của giao thức BB84  |
| `data/benchmark/`       | Lưu trữ dữ liệu đầu vào phục vụ benchmark  |
| `encryption/`           | Mã hóa và giải mã bằng AES-256-GCM            |
| `experiments/`          | Thực hiện các kịch bản và benchmark           |
| `file_transfer/`        | Xử lý truyền tệp và kiểm tra tính toàn vẹn |
| `security/`             | Xử lý khóa và ước lượng QBER                |
| `tests/`                | Chứa các kiểm thử tự động                    |
| `visualization/`        | Xây dựng biểu đồ kết quả                     |
| `config.py`             | Cấu hình các tham số mô phỏng                 |
| `generate_test_data.py` | Tạo dữ liệu phục vụ benchmark                  |
| `main.py`               | Điểm khởi chạy chương trình                  |
| `requirements.txt`      | Danh sách thư viện và phiên bản cần thiết   |

Các kết quả thực nghiệm được lưu trong thư mục `results/` sau khi chạy các chương trình tương ứng. Thư mục này là dữ liệu đầu ra, không phải thành phần bắt buộc để cài đặt mã nguồn.

## 6. Nguyên lý hoạt động của hệ thống

Quy trình mô phỏng BB84 kết hợp AES-256-GCM gồm các bước chính:

1. **Khởi tạo Alice:** Alice sinh chuỗi bit và lựa chọn ngẫu nhiên các cơ sở lượng tử Z/X để chuẩn bị qubit.
2. **Truyền qubit:** Qubit được truyền qua kênh lượng tử mô phỏng.
3. **Mô phỏng Eve:** Eve có thể chặn, đo và gửi lại qubit bằng phương pháp Intercept-Resend theo xác suất tấn công được cấu hình.
4. **Đo tại Bob:** Bob lựa chọn cơ sở đo độc lập và thực hiện phép đo các qubit nhận được.
5. **Sàng lọc khóa:** Alice và Bob so sánh cơ sở đã sử dụng, giữ lại những vị trí có cơ sở trùng khớp.
6. **Ước lượng QBER:** Một phần bit được lấy mẫu để tính tỷ lệ lỗi bit và đánh giá mức độ ảnh hưởng của hành vi nghe lén.
7. **Quyết định phiên:** Nếu QBER vượt ngưỡng cấu hình, phiên bị hủy (ABORT). Nếu đáp ứng điều kiện, hệ thống tiếp tục hậu xử lý khóa.
8. **Mã hóa dữ liệu:** Khóa đầu ra được sử dụng trong quy trình AES-256-GCM để mã hóa dữ liệu.
9. **Giải mã và xác thực:** Hệ thống sử dụng khóa tương ứng để giải mã. Thẻ xác thực GCM được kiểm tra trước khi dữ liệu giải mã được chấp nhận.
10. **Kiểm tra tính toàn vẹn:** SHA-256 được sử dụng để đối chiếu tệp gốc và tệp sau giải mã.

## 7. Cấu hình mô phỏng

Các tham số của hệ thống được quản lý trong tệp `config.py`.

Một số tham số chính bao gồm:

- Số lượng bit/qubit sử dụng trong phiên mô phỏng.
- Seed phục vụ việc sinh dữ liệu giả ngẫu nhiên.
- Trạng thái bật hoặc tắt mô phỏng Eve.
- Xác suất tấn công của Eve.
- Tỷ lệ lấy mẫu để ước lượng QBER.
- Ngưỡng QBER dùng để quyết định tiếp tục hoặc hủy phiên.

Ngưỡng QBER 11% được sử dụng như một tham số minh họa trong phạm vi đề tài, không phải ngưỡng bảo mật phổ quát cho mọi hệ thống BB84.

## 8. Thực nghiệm mô phỏng QBER và tấn công Eve

### 8.1. Mục tiêu

Thực nghiệm khảo sát ảnh hưởng của xác suất tấn công Intercept-Resend đến QBER và tỷ lệ hủy phiên BB84.

Các mức xác suất tấn công được khảo sát từ 0 đến 1. Mỗi mức được thực hiện nhiều lần nhằm đánh giá sự biến thiên của kết quả mô phỏng.

### 8.2. Thực hiện

Chạy thực nghiệm với 10 lần lặp:

```powershell
python -m experiments.scenarios --trials 10
```

Có thể tùy chỉnh số lần lặp và số lượng bit:

```powershell
python -m experiments.scenarios --trials 30 --num-bits 4096
```

Tùy chỉnh tỷ lệ lấy mẫu và ngưỡng QBER:

```powershell
python -m experiments.scenarios --trials 10 --sample-rate 0.2 --threshold 0.11
```

### 8.3. Kết quả

Kết quả thực nghiệm được lưu dưới dạng CSV, bao gồm dữ liệu từng lần chạy và bảng tổng hợp theo xác suất tấn công.

Các biểu đồ được tạo bằng:

```powershell
python -m visualization.charts
```

Các tệp kết quả QBER quan trọng:

- `results/qber_trials.csv`: Kết quả chi tiết từng lần mô phỏng.
- `results/qber_summary.csv`: Kết quả tổng hợp theo xác suất tấn công.
- `results/qber_vs_attack.png`: Biểu đồ quan hệ giữa xác suất tấn công và QBER.
- `results/abort_rate_vs_attack.png`: Biểu đồ tỷ lệ hủy phiên theo xác suất tấn công.

## 9. Dữ liệu và benchmark mã hóa tệp tin

### 9.1. Nguồn dữ liệu

Đề tài không sử dụng dataset bên ngoài từ Kaggle, Google Colab hoặc các nền tảng cung cấp dữ liệu khác.

Dữ liệu benchmark được tự tạo bằng chương trình `generate_test_data.py` và lưu trong thư mục `data/benchmark/`.

Bộ dữ liệu gồm 7 nhóm định dạng:

- `.txt`
- `.docx`
- `.png`
- `.jpg`
- `.wav`
- `.mp3`
- `.mp4`

Mỗi nhóm có 5 mức kích thước:

- 1 KB
- 100 KB
- 1 MB
- 10 MB
- 50 MB

Thông tin dữ liệu và mã băm được quản lý thông qua manifest đi kèm.

**Lưu ý:** Các tệp phi văn bản do chương trình tạo là dữ liệu nhị phân tổng hợp có chữ ký ban đầu, không bảo đảm là tài liệu, hình ảnh, âm thanh hoặc video hợp lệ để mở bằng ứng dụng chuyên dụng. Vì vậy, benchmark tập trung đánh giá khả năng xử lý byte, mã hóa, giải mã và kiểm tra tính toàn vẹn, không đánh giá khả năng hiển thị hoặc phát nội dung bằng phần mềm chuyên dụng.

### 9.2. Tạo dữ liệu benchmark

Để tạo bộ dữ liệu mới:

```powershell
python generate_test_data.py
```

**Lưu ý quan trọng:** Không chạy lại lệnh này nếu muốn giữ nguyên bộ dữ liệu và manifest đã sử dụng trong các lần thực nghiệm trước. Việc tạo lại dữ liệu có thể làm thay đổi nội dung tệp và mã băm tương ứng.

### 9.3. Chạy benchmark

Chạy 10 lần lặp cho mỗi tệp:

```powershell
python -m experiments.file_benchmark --trials 10 --output results/file_benchmark/repeated/file_benchmark_repeated.csv
```

### 9.4. Phân tích kết quả benchmark

```powershell
python -m experiments.analyze_file_benchmark
```

Chương trình phân tích dữ liệu benchmark và tạo các bảng thống kê, phục vụ đánh giá thời gian mã hóa, thời gian giải mã, thông lượng và thời gian xử lý tổng thể.

Một số tệp kết quả quan trọng:

- `results/file_benchmark/repeated/file_benchmark_repeated.csv`: Dữ liệu benchmark chi tiết.
- `results/file_benchmark/repeated/analysis/benchmark_quality_check.csv`: Kiểm tra chất lượng và tính đầy đủ của dữ liệu benchmark.
- `results/file_benchmark/repeated/analysis/benchmark_summary_by_size.csv`: Thống kê theo kích thước tệp.
- `results/file_benchmark/repeated/analysis/benchmark_summary_by_type_size.csv`: Thống kê theo định dạng và kích thước tệp.

Các kết quả benchmark cần được phân tích riêng với thực nghiệm QBER. QBER bằng 0% trong benchmark không chứng minh hệ thống chống được tấn công nghe lén, vì benchmark file được thực hiện trong kịch bản không có tấn công Eve.

## 10. Thực nghiệm trực quan hóa mạch lượng tử Qiskit

Nhánh `experiment/qiskit-aer-enhancement` bổ sung chức năng xuất sơ đồ mạch trực tiếp từ các đối tượng `QuantumCircuit` được sử dụng trong source code. Hình không được vẽ thủ công.

Cài đặt các phụ thuộc đã khai báo:

```powershell
python -m pip install -r requirements.txt
```

Xuất các sơ đồ:

```powershell
python -m visualization.quantum_circuits
```

Các tệp được tạo trong `results/quantum_circuits/`:

- `alice_prepare_x.png`: Alice chuẩn bị trạng thái bit 1 trên cơ sở X.
- `bob_measure_x.png`: Bob đo trên cơ sở X, thể hiện cổng H trước phép đo.
- `eve_intercept_z.png`: Eve đo qubit bị chặn trên cơ sở Z.
- `eve_resend_z.png`: Mạch chuẩn bị qubit mới để gửi lại theo kết quả đo của Eve.
- `circuit_metadata.csv`: Tên mạch, số qubit, số bit cổ điển, các phép toán và backend mô phỏng.

Mạch Eve được thể hiện thành hai giai đoạn riêng: đo qubit nhận được và chuẩn bị qubit gửi lại. Đây là cách phản ánh đúng ranh giới giữa phép đo và việc tạo trạng thái mới trong source hiện tại.

Chạy riêng bộ kiểm thử mới:

```powershell
python -m pytest tests/test_quantum_circuits.py -v
```

CI trên nhánh thử nghiệm cũng xuất sơ đồ và lưu chúng thành artifact của GitHub Actions sau khi kiểm thử hoàn tất.

---

## 11. Kiểm thử tự động

Dự án sử dụng `pytest` để kiểm tra hoạt động của các thành phần quan trọng.

Chạy toàn bộ kiểm thử:

```powershell
python -m pytest -v
```

Các nhóm kiểm thử tập trung vào:

- Sinh và đo qubit.
- Sàng lọc khóa BB84.
- Mô phỏng tấn công Intercept-Resend.
- Ước lượng và kiểm tra QBER.
- Luồng xử lý phiên BB84.
- Xử lý khóa.
- Mã hóa và giải mã AES-256-GCM.
- Truyền tệp và kiểm tra tính toàn vẹn.
- Các trường hợp lỗi và điều kiện đầu vào không hợp lệ.

### 10.1. Kiểm tra môi trường thư viện

```powershell
python -m pip check
```

### 10.2. Tích hợp liên tục với GitHub Actions

Dự án sử dụng GitHub Actions để tự động thực hiện kiểm thử khi có các sự kiện push lên nhánh được cấu hình hoặc tạo pull request.

Tệp cấu hình workflow:

```text
.github/workflows/tests.yml
```

Kết quả thực thi có thể được theo dõi tại mục **Actions** của repository GitHub.

Repository:

https://github.com/lochuynhphuoc/CK

## 12. Giới hạn và lưu ý bảo mật

Dự án có một số giới hạn cần được xem xét khi đánh giá kết quả:

1. **Mô phỏng thay vì thiết bị lượng tử thực tế:** Qubit được mô phỏng bằng Qiskit Aer, không được truyền qua phần cứng lượng tử vật lý.
2. **Nguồn ngẫu nhiên:** Bit và cơ sở được sinh bằng NumPy PRNG, không phải nguồn ngẫu nhiên lượng tử vật lý.
3. **Kênh lượng tử lý tưởng:** Mô hình hiện tại chưa mô phỏng đầy đủ suy hao, nhiễu và các lỗi phát sinh từ thiết bị thực tế.
4. **Kênh cổ điển:** Chưa triển khai cơ chế xác thực mật mã thực tế cho kênh trao đổi thông tin cổ điển giữa Alice và Bob.
5. **Ước lượng QBER:** QBER được tính từ một mẫu hữu hạn nên có sai số thống kê. Kết quả CONTINUE không chứng minh chắc chắn rằng không có Eve.
6. **Information Reconciliation:** Cơ chế sửa lỗi được triển khai ở mức đơn giản phục vụ minh họa, không phải giao thức Cascade hoàn chỉnh.
7. **Privacy Amplification:** Bước khuếch đại riêng tư sử dụng Toeplitz chưa có hạch toán đầy đủ lượng thông tin rò rỉ hoặc phân tích finite-key. Do đó, khóa đầu ra không được xem là khóa QKD có chứng minh an toàn.
8. **Xử lý tệp tin:** Quá trình mã hóa và giải mã hiện đọc toàn bộ tệp vào RAM, chưa tối ưu cho các tệp có dung lượng rất lớn.
9. **Kiểm tra tính toàn vẹn:** SHA-256 được sử dụng để đối chiếu tệp gốc và tệp khôi phục trong thực nghiệm. Việc xác thực mật mã của ciphertext được đảm nhiệm bởi thẻ xác thực AES-GCM.

Các giới hạn trên cho thấy kết quả của đề tài có ý nghĩa minh họa và đánh giá trong phạm vi mô phỏng, không thay thế việc đánh giá an toàn của một hệ thống QKD triển khai thực tế.

## 13. Tài liệu tham khảo và nguồn dữ liệu

### 12.1. Nguồn dữ liệu

Đề tài không sử dụng dataset bên ngoài.

Dữ liệu phục vụ benchmark được sinh trực tiếp từ chương trình:

```text
generate_test_data.py
```

Dữ liệu được lưu trong:

```text
data/benchmark/
```

### 12.2. Mã nguồn dự án

GitHub Repository:

https://github.com/lochuynhphuoc/CK

### 12.3. Tài liệu kỹ thuật

Các tài liệu về giao thức BB84, thuật toán AES, chế độ GCM, Qiskit và các thư viện được sử dụng được liệt kê trong danh mục tài liệu tham khảo của báo cáo đồ án.

## 14. Tiến độ thực hiện

### 13.1. Các chức năng đã triển khai

- [X] Mô phỏng Alice, Bob và kênh lượng tử.
- [X] Triển khai sàng lọc khóa theo giao thức BB84.
- [X] Mô phỏng tấn công Intercept-Resend của Eve.
- [X] Ước lượng QBER và quyết định CONTINUE/ABORT.
- [X] Triển khai các bước hậu xử lý khóa ở mức mô phỏng.
- [X] Tích hợp mã hóa và giải mã AES-256-GCM.
- [X] Hỗ trợ mã hóa và giải mã tệp tin.
- [X] Kiểm tra tính toàn vẹn dữ liệu bằng SHA-256.
- [X] Thực nghiệm QBER theo nhiều mức xác suất tấn công.
- [X] Benchmark mã hóa và giải mã trên nhiều định dạng, kích thước tệp.
- [X] Phân tích và trực quan hóa kết quả thực nghiệm.
- [X] Xây dựng bộ kiểm thử tự động bằng pytest.
- [X] Tích hợp kiểm thử tự động bằng GitHub Actions.

### 13.2. Hướng phát triển

- [ ] Mô phỏng thêm các mô hình nhiễu, suy hao và lỗi thiết bị lượng tử.
- [ ] Nghiên cứu cơ chế xác thực kênh cổ điển.
- [ ] Cải thiện quy trình hậu xử lý khóa.
- [ ] Bổ sung phân tích finite-key và hạch toán thông tin rò rỉ.
- [ ] Tối ưu mã hóa và giải mã tệp tin theo luồng.
- [ ] Mở rộng các kịch bản thực nghiệm và đánh giá trên dữ liệu thực tế.

---

Dự án được xây dựng nhằm minh họa nguyên lý phân phối khóa lượng tử BB84, khả năng phát hiện nghe lén thông qua QBER và việc ứng dụng khóa được xử lý vào mã hóa dữ liệu bằng AES-256-GCM.
