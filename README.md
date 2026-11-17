
# BB84 Quantum Key Distribution Simulator with AES-256-GCM

## 1. Giới thiệu đề tài

**Tên đề tài:** Mô phỏng giao thức phân phối khóa lượng tử BB84 và ứng dụng trong mã hóa dữ liệu AES-256-GCM.

Dự án xây dựng chương trình mô phỏng giao thức BB84 (Bennett–Brassard 1984) nhằm nghiên cứu quá trình phân phối khóa lượng tử giữa hai bên Alice và Bob, đồng thời mô phỏng khả năng phát hiện hành vi nghe lén thông qua tỷ lệ lỗi lượng tử QBER (Quantum Bit Error Rate).

Sau khi hoàn thiện, khóa bí mật được tạo ra từ quá trình BB84 sẽ được xử lý và sử dụng trong thuật toán mã hóa AES-256-GCM để bảo vệ dữ liệu.

Chương trình được xây dựng bằng Python, sử dụng Qiskit và Qiskit Aer để mô phỏng hoạt động của qubit và quá trình đo lượng tử.

## 2. Mục tiêu

- Tìm hiểu nguyên lý hoạt động của giao thức phân phối khóa lượng tử BB84.
- Mô phỏng quá trình tạo, truyền và đo qubit.
- Mô phỏng quá trình lựa chọn cơ sở và sàng lọc khóa giữa Alice và Bob.
- Mô phỏng tấn công nghe lén Intercept-Resend của Eve.
- Tính toán QBER để đánh giá mức độ bất thường trong quá trình truyền khóa.
- Xây dựng cơ chế quyết định tiếp tục hoặc hủy phiên trao đổi khóa dựa trên ngưỡng QBER.
- Nghiên cứu xử lý khóa và ứng dụng khóa được phân phối trong AES-256-GCM.
- Thực hiện các kịch bản thử nghiệm và đánh giá kết quả mô phỏng.

## 3. Công nghệ sử dụng

| Công nghệ  | Mục đích                                       |
| ------------ | ------------------------------------------------- |
| Python       | Ngôn ngữ lập trình chính                     |
| Qiskit       | Xây dựng và thao tác với mạch lượng tử   |
| Qiskit Aer   | Mô phỏng quá trình đo qubit                  |
| NumPy        | Sinh dữ liệu ngẫu nhiên và xử lý dữ liệu |
| PyCryptodome | Triển khai AES-256-GCM                           |
| Matplotlib   | Trực quan hóa kết quả thực nghiệm           |

## 4. Kiến trúc dự án

```text
CK/
│
├── attack/
│   ├── __init__.py
│   └── eve.py
│
├── bb84/
│   ├── __init__.py
│   ├── alice.py
│   ├── bob.py
│   ├── key_sifting.py
│   └── quantum_channel.py
│
├── encryption/
│   ├── __init__.py
│   └── aes_gcm.py
│
├── experiments/
│   ├── __init__.py
│   ├── results.py
│   └── scenarios.py
│
├── security/
│   ├── __init__.py
│   ├── key_processing.py
│   └── qber.py
│
├── tests/
│   ├── __init__.py
│   ├── test_aes.py
│   ├── test_bb84.py
│   ├── test_eve.py
│   └── test_qber.py
│
├── visualization/
│   ├── __init__.py
│   └── charts.py
│
├── config.py
├── main.py
├── README.md
└── requirements.txt
```

## 5. Mô tả các thành phần

### 5.1. Module BB84 (`bb84/`)

| File                   | Chức năng                                                                                                             |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `alice.py`           | Sinh bit ngẫu nhiên, lựa chọn cơ sở Z/X và chuẩn bị trạng thái qubit.                                        |
| `bob.py`             | Lựa chọn cơ sở đo và thực hiện phép đo qubit bằng Qiskit Aer.                                                |
| `quantum_channel.py` | Mô phỏng quá trình truyền qubit từ Alice đến Bob.                                                               |
| `key_sifting.py`     | So sánh cơ sở của Alice và Bob, giữ lại những vị trí có cơ sở trùng khớp để tạo khóa sau sàng lọc. |

### 5.2. Module tấn công (`attack/`)

| File       | Chức năng                                                                                                                                              |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `eve.py` | Mô phỏng tấn công Intercept-Resend. Eve chặn qubit, lựa chọn cơ sở đo ngẫu nhiên, đo trạng thái và chuẩn bị qubit mới gửi đến Bob. |

### 5.3. Module bảo mật (`security/`)

| File                  | Chức năng                                                                                                               |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `qber.py`           | Lấy mẫu khóa sau sàng lọc, tính QBER và quyết định tiếp tục hoặc hủy phiên dựa trên ngưỡng cấu hình. |
| `key_processing.py` | Dự kiến triển khai xử lý khóa, sửa lỗi và khuếch đại riêng tư trước khi sử dụng cho AES.                |

### 5.4. Module mã hóa (`encryption/`)

| File           | Chức năng                                                                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `aes_gcm.py` | Dự kiến triển khai mã hóa và giải mã dữ liệu bằng AES-256-GCM, đồng thời kiểm tra tính toàn vẹn và xác thực dữ liệu. |

### 5.5. Module thực nghiệm (`experiments/`)

| File             | Chức năng                                                                                   |
| ---------------- | --------------------------------------------------------------------------------------------- |
| `scenarios.py` | Dự kiến thiết lập các kịch bản mô phỏng với những mức độ tấn công khác nhau. |
| `results.py`   | Dự kiến tổng hợp và lưu kết quả thực nghiệm.                                        |

### 5.6. Module trực quan hóa (`visualization/`)

| File          | Chức năng                                                                               |
| ------------- | ----------------------------------------------------------------------------------------- |
| `charts.py` | Dự kiến xây dựng biểu đồ thể hiện QBER và kết quả các kịch bản mô phỏng. |

### 5.7. Module kiểm thử (`tests/`)

| File             | Chức năng                                                                |
| ---------------- | -------------------------------------------------------------------------- |
| `test_bb84.py` | Kiểm thử các chức năng của giao thức BB84.                          |
| `test_eve.py`  | Kiểm thử mô hình tấn công Intercept-Resend.                          |
| `test_qber.py` | Kiểm thử quá trình tính toán QBER.                                   |
| `test_aes.py`  | Dự kiến kiểm thử mã hóa, giải mã và xác thực dữ liệu AES-GCM. |

### 5.8. File cấu hình và chương trình chính

- `config.py`: Quản lý các thông số mô phỏng như số lượng bit, seed ngẫu nhiên, trạng thái Eve, tỷ lệ tấn công và ngưỡng QBER.
- `main.py`: Chương trình chính, điều phối các module và hiển thị kết quả mô phỏng.

## 6. Nguyên lý hoạt động

### 6.1. Tạo và chuẩn bị qubit

Alice tạo chuỗi bit ngẫu nhiên gồm 0 và 1, đồng thời lựa chọn ngẫu nhiên một trong hai cơ sở:

- Cơ sở Z: {|0⟩, |1⟩}.
- Cơ sở X: {|+⟩, |−⟩}.

Alice sử dụng các cổng lượng tử để chuẩn bị trạng thái qubit tương ứng với bit và cơ sở đã chọn.

### 6.2. Truyền qubit

Các qubit được truyền qua kênh lượng tử đến Bob.

Trong mô hình hiện tại, quá trình truyền được mô phỏng bằng các mạch lượng tử trên Qiskit Aer.

### 6.3. Mô phỏng Eve

Eve có thể thực hiện tấn công Intercept-Resend:

1. Chặn qubit trên kênh truyền.
2. Chọn ngẫu nhiên cơ sở Z hoặc X.
3. Đo trạng thái qubit.
4. Chuẩn bị một qubit mới dựa trên kết quả đo.
5. Gửi qubit mới đến Bob.

Việc Eve lựa chọn sai cơ sở có thể làm thay đổi trạng thái lượng tử và tạo ra lỗi trong kết quả đo của Bob.

### 6.4. Đo qubit và sàng lọc khóa

Bob lựa chọn ngẫu nhiên cơ sở đo cho từng qubit.

Sau khi đo, Alice và Bob công khai cơ sở đã sử dụng thông qua kênh cổ điển để xác định những vị trí có cơ sở trùng khớp.

Các vị trí không trùng khớp sẽ bị loại bỏ. Những vị trí còn lại tạo thành khóa sau sàng lọc (Sifted Key).

### 6.5. Ước lượng QBER

Alice và Bob công khai một phần bit được chọn ngẫu nhiên từ khóa sau sàng lọc để so sánh.

QBER được tính theo công thức:

\[
QBER = \frac{N_{\text{error}}}{N_{\text{sample}}}\times100\%
\]

Trong đó:

- \(N_{\text{error}}\): Số bit khác nhau trong mẫu kiểm tra.
- \(N_{\text{sample}}\): Tổng số bit được lấy mẫu.

Nếu QBER vượt ngưỡng cấu hình, phiên trao đổi khóa sẽ bị hủy. Nếu QBER nằm trong ngưỡng, chương trình cho phép tiếp tục xử lý khóa.

**Lưu ý:** Ngưỡng QBER trong chương trình hiện tại chỉ phục vụ mục đích mô phỏng và minh họa, không phải ngưỡng bảo mật phổ quát cho mọi hệ thống BB84.

### 6.6. Xử lý khóa và mã hóa AES

Đây là phần đang được phát triển.

Dự kiến quy trình gồm:

1. Thực hiện sửa lỗi để Alice và Bob thống nhất khóa.
2. Thực hiện khuếch đại riêng tư nhằm giảm thông tin mà Eve có thể biết.
3. Kiểm tra độ dài và điều kiện an toàn của khóa.
4. Sử dụng khóa bí mật 256 bit làm khóa AES-256-GCM.
5. Mã hóa và giải mã dữ liệu.
6. Kiểm tra tính toàn vẹn và xác thực dữ liệu thông qua authentication tag.

Nếu lượng khóa bí mật còn lại không đủ hoặc không đáp ứng điều kiện xử lý, chương trình phải từ chối tạo khóa AES.

## 7. Kết quả mô phỏng hiện tại

Chương trình đã thực hiện thử nghiệm với cấu hình:

| Thông số              | Giá trị |
| ----------------------- | --------: |
| Số qubit truyền       |       256 |
| Cơ sở sử dụng       |   Z và X |
| Tỷ lệ lấy mẫu QBER  |       20% |
| Ngưỡng QBER minh họa |       11% |

### Kịch bản 1: Không có Eve

| Thông số                     | Kết quả |
| ------------------------------ | --------: |
| Tổng số qubit                |       256 |
| Cơ sở trùng khớp           |       138 |
| Bit bị loại                  |       118 |
| Độ dài khóa sau sàng lọc |       138 |
| Số bit lấy mẫu              |        28 |
| Số lỗi                       |         0 |
| QBER                           |        0% |
| Trạng thái                   |  CONTINUE |

Kết quả cho thấy trong mô hình kênh lý tưởng không có Eve, Alice và Bob thu được kết quả đo giống nhau tại các vị trí có cơ sở trùng khớp.

### Kịch bản 2: Eve tấn công 100%

| Thông số                     | Kết quả |
| ------------------------------ | --------: |
| Tổng số qubit                |       256 |
| Tỷ lệ tấn công cấu hình  |      100% |
| Số qubit bị Eve chặn        |       256 |
| Cơ sở trùng khớp           |       138 |
| Độ dài khóa sau sàng lọc |       138 |
| Số bit lấy mẫu              |        28 |
| Số lỗi trong mẫu            |         5 |
| QBER ước lượng             |    17,86% |
| Ngưỡng QBER                  |       11% |
| Trạng thái                   |     ABORT |

Kết quả cho thấy tỷ lệ lỗi trong mẫu vượt ngưỡng cấu hình, do đó chương trình quyết định hủy phiên trao đổi khóa.

Theo lý thuyết BB84, tấn công Intercept-Resend với cơ sở đo ngẫu nhiên có thể tạo ra QBER kỳ vọng khoảng 25% trên khóa đã sàng lọc trong mô hình lý tưởng. Kết quả thực nghiệm có thể dao động do số lượng bit lấy mẫu hữu hạn.

## 8. Cài đặt môi trường

### 8.1. Yêu cầu

- Python 3.10 trở lên.
- pip.
- Môi trường ảo Python (khuyến nghị).

### 8.2. Tạo môi trường ảo

Windows PowerShell:

```powershell
python -m venv .venv
```

Kích hoạt môi trường:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 8.3. Cài đặt thư viện

```powershell
pip install -r requirements.txt
```

## 9. Cách chạy chương trình

Tại thư mục gốc của dự án, thực hiện:

```powershell
python main.py
```

Các thông số mô phỏng được điều chỉnh trong `config.py`.

Ví dụ:

```python
NUM_BITS = 256

ENABLE_EVE = True
EVE_ATTACK_PROBABILITY = 1.0

QBER_SAMPLE_RATE = 0.20
QBER_THRESHOLD = 0.11
```

Một số cấu hình thử nghiệm:

- Không có Eve: `ENABLE_EVE = False`.
- Eve tấn công 50%: `ENABLE_EVE = True`, `EVE_ATTACK_PROBABILITY = 0.5`.
- Eve tấn công 100%: `ENABLE_EVE = True`, `EVE_ATTACK_PROBABILITY = 1.0`.

## 10. Tiến độ thực hiện

### Đã triển khai và kiểm tra

- [X] Tạo cấu trúc dự án.
- [X] Cấu hình môi trường Python.
- [X] Sinh bit và cơ sở ngẫu nhiên cho Alice.
- [X] Chuẩn bị qubit bằng Qiskit.
- [X] Mô phỏng kênh truyền lượng tử.
- [X] Sinh cơ sở đo và đo qubit cho Bob.
- [X] Sàng lọc khóa giữa Alice và Bob.
- [X] Mô phỏng tấn công Intercept-Resend của Eve.
- [X] Tính toán QBER bằng phương pháp lấy mẫu.
- [X] Quyết định CONTINUE hoặc ABORT dựa trên ngưỡng QBER.
- [X] Chạy thử nghiệm không có Eve.
- [X] Chạy thử nghiệm Eve tấn công 100%.

### Đang phát triển

- [ ] Triển khai xử lý khóa sau sàng lọc.
- [ ] Triển khai Information Reconciliation.
- [ ] Triển khai Privacy Amplification.
- [ ] Tạo khóa bí mật 256 bit đủ điều kiện sử dụng.
- [ ] Triển khai mã hóa AES-256-GCM.
- [ ] Triển khai giải mã và xác thực dữ liệu.
- [ ] Kiểm tra trường hợp dữ liệu bị chỉnh sửa.
- [ ] Tích hợp BB84 và AES vào chương trình chính.
- [ ] Xây dựng các kịch bản thực nghiệm tự động.
- [ ] Lưu kết quả thực nghiệm.
- [ ] Xây dựng biểu đồ trực quan hóa.
- [ ] Hoàn thiện kiểm thử và tài liệu dự án.

## 11. Giới hạn của mô hình

Đây là chương trình mô phỏng phục vụ mục đích học tập và nghiên cứu, không phải hệ thống QKD triển khai trong môi trường thực tế.

Một số giới hạn hiện tại:

- Chưa mô phỏng thiết bị lượng tử vật lý.
- Kênh lượng tử hiện tại chưa tích hợp nhiễu hoặc suy hao thực tế.
- Kênh cổ điển chưa triển khai cơ chế xác thực mật mã thực tế.
- QBER được ước lượng bằng mẫu hữu hạn nên có sai số thống kê.
- Chưa triển khai đầy đủ quy trình xử lý khóa và phân tích bảo mật hữu hạn.
- Chưa thể sử dụng khóa sau sàng lọc trực tiếp làm khóa AES.

## 12. Định hướng phát triển

- Hoàn thiện quy trình xử lý khóa BB84.
- Tích hợp AES-256-GCM để mã hóa và giải mã dữ liệu.
- Bổ sung nhiều mức độ tấn công của Eve.
- Thử nghiệm với nhiều số lượng qubit khác nhau.
- Phân tích mối quan hệ giữa tỷ lệ tấn công và QBER.
- Xây dựng biểu đồ và bảng kết quả thực nghiệm.
- Hoàn thiện kiểm thử, đánh giá và tài liệu báo cáo.

---

**Trạng thái dự án:** Đang phát triển.

**Mục tiêu cuối cùng:** Xây dựng chương trình mô phỏng quy trình phân phối khóa lượng tử BB84, đánh giá khả năng phát hiện nghe lén và ứng dụng khóa bí mật thu được vào mã hóa dữ liệu AES-256-GCM.
