# BÁO CÁO TỔNG HỢP ĐIỀU PHỐI KHÁCH HÀNG TIỀM NĂNG
## CÔNG TY PHẦN MỀM NAM VIỆT - HỆ THỐNG AI AGENT ĐIỀU PHỐI (AI301 - ĐỀ 02)

---

### 1. Tổng Quan Chỉ Số Xử Lý (Lead Processing Metrics)
- **Tổng số hồ sơ tiếp nhận ban đầu (Raw Leads):** `20` hồ sơ.
- **Tổng số khách hàng duy nhất sau khử trùng (Master Customers):** `18` doanh nghiệp.
- **Tỷ lệ giảm tải trùng lặp (Deduplication Rate):** `10.0%`.
- **Số hồ sơ chuyển Trưởng phòng Kinh doanh xem xét (Escalations):** `5` khách hàng.
- **Số hồ sơ chặn theo lịch sử (Do Not Contact):** `1` khách hàng.
- **Số khách hàng hiện hữu chuyển sang CSKH/Account Manager:** `1` khách hàng.

---

### 2. Phân Bổ Mức Độ Ưu Tiên (Khách Hàng Duy Nhất - Không Đếm Lặp)
| Phân loại ưu tiên | Ý nghĩa nghiệp vụ | Số lượng (KH duy nhất) | Tỷ lệ (%) |
| :--- | :--- | :---: | :---: |
| **P1 - Hot Lead** | Nhu cầu khớp sản phẩm, ngân sách chuẩn, liên hệ cấp lãnh đạo (Cần gọi trong 2h) | `14` | `77.8%` |
| **P2 - Warm Lead** | Nhu cầu rất phù hợp, cần phỏng vấn bổ sung thông tin thiếu (Gọi trong 8h) | `0` | `0.0%` |
| **P3 - Cold Lead** | Nhu cầu chung chung / vãng lai, gửi tài liệu cẩm nang nuôi dưỡng | `1` | `5.6%` |
| **Out-of-Scope** | Ngân sách lớn hoặc yêu cầu ngoài dòng sản phẩm Nam Việt (Gia công, Drone...) | `1` | `5.6%` |
| **Do Not Contact** | Khách hàng lịch sử yêu cầu không làm phiền / Blacklist (Tuyệt đối không gọi) | `1` | `5.6%` |
| **Active Client** | Khách hàng hiện hữu cần mở rộng / hỗ trợ dịch vụ -> Chuyển CSKH | `1` | `5.6%` |

---

### 3. Phân Phối Tải Công Việc Cho 8 Nhân Viên Kinh Doanh (Không Đếm Lặp)
| Mã NVKD | Họ và tên NVKD | Nhóm ngành phụ trách | Khu vực | Tổng số KH nhận | P1 (Hot) | P2 (Warm) | P3 (Cold) |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `SALE-01` | **Nguyễn Văn An** | Sản xuất, Xây dựng, Cơ khí | Miền Bắc | **2** | 2 | 0 | 0 |
| `SALE-02` | **Trần Thị Bình** | Bán lẻ, Thương mại điện tử, Thời trang | Miền Bắc | **3** | 3 | 0 | 0 |
| `SALE-03` | **Lê Hoàng Cường** | F&B, Khách sạn, Dịch vụ | Miền Bắc | **1** | 1 | 0 | 0 |
| `SALE-04` | **Phạm Thu Dung** | Logistics, Vận tải, Kho bãi, Phân phối | Miền Trung, Toàn quốc | **1** | 1 | 0 | 0 |
| `SALE-05` | **Hoàng Minh Đức** | Sản xuất, Xây dựng, Vật liệu xây dựng | Miền Nam | **1** | 1 | 0 | 0 |
| `SALE-06` | **Đỗ Mai Hoa** | Bán lẻ, Chuỗi cửa hàng, Mỹ phẩm, Thương mại điện tử | Miền Nam | **1** | 1 | 0 | 0 |
| `SALE-07` | **Vũ Quốc Hùng** | Dịch vụ, Giáo dục, Y tế, Công nghệ | Miền Nam | **2** | 1 | 0 | 0 |
| `SALE-08` | **Đặng Thùy Linh** | F&B, Nông sản, Dịch vụ tổng hợp | Miền Trung, Miền Nam, Toàn quốc | **2** | 2 | 0 | 0 |

---
*Báo cáo được tự động khởi tạo bởi NamViet AI Lead Dispatcher Engine.*
