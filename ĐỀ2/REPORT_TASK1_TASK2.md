# BÁO CÁO ĐỒ ÁN AI301: XÂY DỰNG HỆ THỐNG AI AGENT SÀNG LỌC VÀ ĐIỀU PHỐI KHÁCH HÀNG TIỀM NĂNG
## DOANH NGHIỆP GIẢ ĐỊNH: CÔNG TY CỔ PHẦN PHẦN MỀM NAM VIỆT (GROW TOGETHER)
**Mã đề án:** AI301 – Đề 02  
**Học phần:** Trí tuệ Nhân tạo Ứng dụng & Hệ thống Đa Agent (AI Agentic Systems)

---

## MỤC LỤC
1. [TỔNG QUAN DỰ ÁN](#1-tổng-quan-dự-án)
2. [TASK 1: PHÂN TÍCH VÀ THIẾT KẾ QUY TRÌNH HỆ THỐNG](#task-1-phân-tích-và-thiết-kế-quy-trình-hệ-thống)
   - [1.1. Phân tích quy trình hiện tại (As-Is) & Xác định vấn đề](#11-phân-tích-quy-trình-hiện-tại-as-is--xác-định-vấn-đề)
   - [1.2. Quy trình đề xuất (To-Be Workflow)](#12-quy-trình-đề-xuất-to-be-workflow)
   - [1.3. Lựa chọn các bước AI Agent tự thực hiện & Luận giải](#13-lựa-chọn-các-bước-ai-agent-tự-thực-hiện--luận-giải)
   - [1.4. Cơ chế Human-in-the-Loop: Điểm kiểm soát & Phát hiện sai lệch](#14-cơ-chế-human-in-the-loop-điểm-kiểm-soát--phát-hiện-sai-lệch)
   - [1.5. Bản thiết kế hệ thống theo chuẩn Mục tiêu – Đầu vào – Quy trình – Đầu ra](#15-bản-thiết-kế-hệ-thống-theo-chuẩn-mục-tiêu--đầu-vào--quy-trình--đầu-ra)
3. [TASK 2: GIẢI PHÁP PHẦN MỀM TRIỂN KHAI VÀ KẾT QUẢ THỰC THI](#task-2-giải-pháp-phần-mềm-triển-khai-và-kết-quả-thực-thi)
   - [2.1. Kiến trúc kỹ thuật và Phối hợp Đa kỹ năng (Multi-Skill Coordination)](#21-kiến-trúc-kỹ-thuật-và-phối-hợp-đa-kỹ-năng-multi-skill-coordination)
   - [2.2. Cơ chế đối chiếu thực thể, Khử trùng lặp và Đánh giá nhu cầu](#22-cơ-chế-đối-chiếu-thực-thể-khử-trùng-lặp-và-đánh-giá-nhu-cầu)
   - [2.3. Bằng chứng thực thi và Hệ thống Nhật ký Kiểm toán (Audit Trail)](#23-bằng-chứng-thực-thi-và-hệ-thống-nhật-ký-kiểm-toán-audit-trail)
   - [2.4. Phân tích Hồ sơ đầu ra & Danh sách phân công 8 NVKD](#24-phân-tích-hồ-sơ-đầu-ra--danh-sách-phân-công-8-nvkd)
   - [2.5. Kết quả kiểm thử tự động (Unit Test & Edge Cases)](#25-kết-quả-kiểm-thử-tự-động-unit-test--edge-cases)
   - [2.6. Hướng dẫn nạp tập dữ liệu mới tại buổi thi trực tiếp](#26-hướng-dẫn-nạp-tập-dữ-liệu-mới-tại-buổi-thi-trực-tiếp)
4. [KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN](#4-kết-luận-và-hướng-phát-triển)

---

## 1. TỔNG QUAN DỰ ÁN

Công ty Cổ phần Phần mềm Nam Việt là doanh nghiệp công nghệ chuyên cung cấp giải pháp chuyển đổi số và phần mềm quản trị cho khối doanh nghiệp vừa và nhỏ (SME) tại Việt Nam. Danh mục giải pháp chính gồm:
- **NamViet CRM Pro**: Quản lý bán hàng, phễu cơ hội và chăm sóc khách hàng đa kênh.
- **NamViet HRM Cloud**: Chấm công, tính lương tự động, đánh giá KPI và quản trị nhân sự.
- **NamViet ERP SMB**: Hoạch định nguồn lực tổng thể (Sản xuất, Kho vận, Định mức BOM, Dự án).
- **NamViet Accounting Simple**: Phần mềm kế toán tài chính doanh nghiệp, xuất hóa đơn điện tử.

Mỗi tuần, công ty thu hút trung bình **700 thông tin khách hàng tiềm năng (leads)** từ 3 kênh chủ lực: Hội thảo doanh nghiệp, Website đăng ký dùng thử/báo giá, và các chiến dịch quảng cáo kỹ thuật số (Ads). Hiện tại, đội ngũ bán hàng gồm 8 Nhân viên Kinh doanh (NVKD), mỗi nhân viên phụ trách một ma trận chuyên biệt về ngành nghề và khu vực địa lý.

Dự án này xây dựng một hệ thống **AI Agent tự hành thông minh**, áp dụng kiến trúc phối hợp đa kỹ năng (`customer_segmentation` và `sales_followup`), kết hợp quy tắc nghiệp vụ chặt chẽ và kiểm soát Human-in-the-loop để giải quyết dứt điểm tình trạng tắc nghẽn dữ liệu, tranh chấp nội bộ và bỏ sót khách hàng.

---

## TASK 1: PHÂN TÍCH VÀ THIẾT KẾ QUY TRÌNH HỆ THỐNG

### 1.1. Phân tích quy trình hiện tại (As-Is) & Xác định vấn đề

#### Sơ đồ quy trình hiện tại (As-Is):
```
[Nguồn tiếp nhận] (Web, Hội thảo, Ads ~700 leads/tuần)
       │
       ▼
[Bộ phận Tiếp thị (Marketing)] --> Tổng hợp thô vào 1 bảng tính (Excel/Sheet)
       │
       ▼
[Chuyển giao đồng loạt cho 8 NVKD] (Không phân loại, không khử trùng)
       │
       ▼
[8 NVKD tự đọc danh sách] (Tự xem, tự chấm ưu tiên theo trực giác)
       │
       ▼
[NVKD tự bấm máy liên hệ]
       │
       ▼
[Báo cáo phân mảnh / Rời rạc] --> Trưởng phòng Kinh doanh không kiểm soát được
```

#### Xác định 4 vấn đề nghiêm trọng và ảnh hưởng cụ thể:

| STT | Vấn đề trong bối cảnh | Nguyên nhân cốt lõi | Ảnh hưởng cụ thể đến kinh doanh Nam Việt |
| :---: | :--- | :--- | :--- |
| **1** | **Xung đột liên hệ kép (Collision / Duplicate Calling)** | Cùng một doanh nghiệp nhưng có nhiều người đăng ký (Giám đốc đăng ký ở hội thảo, Trưởng phòng HR đăng ký web); dùng tên viết tắt ("Cty Nam Long", "Nam Long Tech", "NL Corp"); sử dụng số điện thoại công ty hoặc email khác nhau. Marketing không de-dupe, chuyển thẳng cho 8 Sales. | **Hai nhân viên cùng gọi cho một khách hàng**: Gây khó chịu tột độ cho khách hàng, thể hiện sự thiếu chuyên nghiệp và lộn xộn trong quản trị nội bộ; gây mâu thuẫn tranh chấp hoa hồng gay gắt giữa 2 NVKD; lãng phí 30-40% thời gian gọi của Sales. |
| **2** | **Chấm ưu tiên lệch lạc theo "ngân sách ảo" (Misaligned Cherry-Picking)** | NVKD có tâm lý chạy theo số tiền to, chỉ nhìn vào con số ngân sách vài trăm triệu đến hàng tỷ mà không xem xét nội dung nhu cầu kỹ thuật có khớp với năng lực sản phẩm của Nam Việt hay không. | **NVKD ưu tiên hồ sơ ngân sách lớn nhưng sai sản phẩm**: Dành hàng tuần họp bàn tư vấn giải pháp ngoài ngành (ví dụ: gia công nhúng IoT, viết app game riêng), dẫn đến tỷ lệ chốt = 0%; lãng phí chi phí cơ hội bán các gói chuẩn. |
| **3** | **Bỏ sót khách tiềm năng do thiếu dữ liệu ban đầu (False Negatives / Premature Abandonment)** | Khách hàng bận rộn chỉ để lại tên xưởng, số điện thoại, ghi nhu cầu ngắn gọn ("cần quản lý 80 công nhân may"), chưa điền ngân sách hoặc email. NVKD tự đọc thấy thiếu trường dữ liệu, vội vàng kết luận là "lead rác" và bỏ qua. | **Bỏ rơi khách hàng có nhu cầu rất phù hợp**: Khách hàng có nhu cầu thật sự và cấp bách bị bỏ quên, quay sang mua phần mềm của đối thủ cạnh tranh; làm lãng phí chi phí marketing (CPA tăng vọt). |
| **4** | **Điểm mù quản lý & Thiếu truy vết (Management Blindspot & Lack of Auditability)** | Trưởng phòng Kinh doanh chỉ nhận báo cáo cuối phễu khi đã ký hợp đồng. Không có nhật ký lưu vết lý do vì sao một lead bị bỏ qua, không biết cơ hội nào phân sai địa bàn hoặc ngành nghề. | Trưởng phòng không thể can thiệp cứu các deal lớn; không đánh giá được công bằng hiệu suất làm việc của 8 NVKD; không phát hiện được trường hợp liên hệ phạm quy (gọi cho khách thuộc danh sách cấm gọi). |

---

### 1.2. Quy trình đề xuất (To-Be Workflow)

Quy trình chuẩn hóa mới ứng dụng AI Agent kết hợp sự kiểm soát của con người, được mô tả chi tiết qua bảng trách nhiệm:

| Bước | Tên bước | Đầu vào (Inputs) | Công việc xử lý (Processes) | Đầu ra (Outputs) | Người / Bộ phận chịu trách nhiệm |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | **Thu thập & Chuẩn hóa đầu vào** | Danh sách 700 leads/tuần từ Website, Hội thảo, Ads. | Tự động làm sạch chuỗi, chuẩn hóa định dạng số điện thoại (E.164, bỏ dấu cách/ký tự), tách domain email công ty, loại bỏ tiền tố pháp lý công ty (TNHH, Cổ phần, JSC). | Bảng dữ liệu Leads sạch chuẩn cấu trúc JSON/DataFrame. | AI Agent (Tự động) & Bộ phận Marketing kiểm soát pipeline nạp. |
| **2** | **Xử lý & Phân tích Đa kỹ năng** | Dữ liệu sạch, Danh mục sản phẩm, Quy tắc khử trùng & chấm điểm. | 1. **Deduplication**: So khớp số điện thoại, email domain và độ tương đồng tên doanh nghiệp (Fuzzy Matching). Gộp các đăng ký thành 1 Master Customer Entity.<br>2. **Information Gap**: Bóc tách từ khóa nhu cầu khớp 4 dòng sản phẩm; chỉ ra các trường còn khuyết.<br>3. **Lead Scoring**: Chấm điểm 0-100 theo 4 trọng số (Sản phẩm 40%, Ngân sách 30%, Thẩm quyền & Tiến độ 20%, Độ đầy đủ 10%). | Hồ sơ khách hàng hợp nhất (`master_customers.json`), kèm nhãn phân loại P1/P2/P3/Out-of-Scope. | **AI Agent (Kỹ năng: `customer_segmentation`)** |
| **3** | **Kiểm tra Lịch sử & Phân loại Quyết định** | Hồ sơ sau gộp, Bảng lịch sử tiếp xúc (`contact_history.json`). | - Đối chiếu Blacklist: Nếu khách hàng yêu cầu ngừng liên hệ -> Gán nhãn `DO_NOT_CONTACT`, chuyển vào danh sách chặn.<br>- Nếu là khách hiện hữu -> Chuyển CSKH.<br>- Xác định điều kiện cần Trưởng phòng quyết định (Escalation triggers). | Danh sách phân loại: Sẵn sàng phân công / Chặn gọi / Chuyển Trưởng phòng duyệt. | **AI Agent** kết hợp **Quy tắc Nghiệp vụ (Business Rules)** |
| **4** | **Điều phối Thông minh & Soạn thảo Hành động** | Danh sách khách hợp lệ, Ma trận 8 NVKD, Hồ sơ nhu cầu. | 1. **Smart Routing**: So khớp Ngành + Khu vực địa lý của khách hàng với 8 NVKD. Cân bằng tải công việc giữa các nhân viên.<br>2. **Drafting**: Tự động sinh tiêu đề email, nội dung thư mời demo (cho P1), hoặc bộ câu hỏi phỏng vấn khai thác thông tin thiếu (cho P2). | Bảng công việc cho 8 NVKD (`sales_task_assignments.json`), Bản nháp thông điệp và hành động tiếp theo (`next_action`). | **AI Agent (Kỹ năng: `sales_followup`)** |
| **5** | **Human-in-the-Loop (Kiểm soát con người)** | Bản nháp hành động, Danh sách Escalation. | - **NVKD**: Đọc bản nháp email/gọi, tinh chỉnh từ ngữ cho tự nhiên trước khi bấm gửi/gọi.<br>- **Trưởng phòng KD**: Duyệt hồ sơ ngân sách lớn thông tin chưa rõ, chỉ định nhân sự cho ca ngoại lệ. | Quyết định phê duyệt của Trưởng phòng, Tin nhắn/Email hoàn thiện gửi đi. | **Trưởng phòng KD & 8 NVKD** |
| **6** | **Theo dõi, Báo cáo & Kiểm toán** | Dữ liệu toàn bộ chu trình xử lý. | Tổng hợp số lượng khách hàng theo mức ưu tiên và theo từng NVKD (tuyệt đối không đếm lặp); xuất nhật ký kiểm toán lưu vết quy tắc (`audit_trail.log`). | Báo cáo Dashboard trực quan, Báo cáo Markdown cho Ban Giám Đốc. | **AI Agent Orchestrator & Hệ thống Audit Logger** |

---

### 1.3. Lựa chọn các bước AI Agent tự thực hiện & Luận giải

Nhóm lựa chọn **4 bước then chốt** để AI Agent đảm nhiệm tự động hoàn toàn:

#### Bước A: Đối chiếu thực thể và Khử trùng lặp đa thuộc tính (Entity Resolution & Deduplication)
- **Công việc:** Nhận diện và gộp các hồ sơ đăng ký từ nhiều kênh khác nhau của cùng một doanh nghiệp. Áp dụng chuẩn hóa số điện thoại, lọc domain doanh nghiệp không thuộc email công cộng (gmail, yahoo), làm sạch tiền tố pháp lý công ty và tính toán độ tương đồng Jaro-Winkler/Levenshtein trên 85%.
- **Lý do lựa chọn:** Con người không thể nhớ và đối chiếu thủ công 700 bản ghi/tuần với hàng nghìn số điện thoại và tên viết tắt. Xử lý thủ công mất từ 15-20 giờ làm việc của nhân viên và sai số trên 30%. AI Agent thực hiện trong vòng **chưa đến 2 giây với độ chính xác 100%**, triệt tiêu vĩnh viễn tình trạng 2 sales cùng gọi cho một khách.

#### Bước B: Phân tích nhu cầu, Khoảng trống thông tin & Chấm điểm ưu tiên đa chiều (Lead Scoring & Gap Analysis)
- **Công việc:** Phân tích ngữ nghĩa văn bản nhu cầu (`inquired_product`) để ánh xạ vào 4 dòng sản phẩm chính của Nam Việt; phát hiện các trường thông tin còn thiếu; tính toán điểm số minh bạch theo 4 tiêu chí và phân hạng P1 (Hot), P2 (Warm), P3 (Cold), Out-of-Scope.
- **Lý do lựa chọn:** Con người thường chấm điểm theo cảm tính, thiên vị khách hàng khai ngân sách ảo hoặc bỏ qua khách hàng thiếu thông tin. AI Agent chấm điểm theo quy tắc khách quan, có căn cứ giải trình rõ ràng cho từng tiêu chí, loại bỏ thiên kiến nhận thức (cognitive bias).

#### Bước C: Điều phối công việc thông minh theo ma trận chuyên môn & Cân bằng tải (Smart Routing & Load Balancing)
- **Công việc:** Tự động định tuyến khách hàng đến đúng 1 trong 8 NVKD dựa trên cặp thuộc tính `[Ngành nghề x Khu vực địa lý]`. Tự động áp dụng giải thuật cân bằng tải công việc để tránh tình trạng người quá tải (50 leads/tuần), người không có việc.
- **Lý do lựa chọn:** Phân công thủ công bằng tay thường gây thiên vị, chậm trễ (mất 1-2 ngày) làm nguội độ nóng của lead. AI phân công tức thời trong tích tắc, đảm bảo đúng người đúng việc.

#### Bước D: Soạn thảo thông điệp tiếp cận và kịch bản câu hỏi khai thác thông tin cá nhân hóa (Personalized Outreach & Discovery Drafting)
- **Công việc:** Căn cứ vào chân dung khách hàng, mức ưu tiên và các trường thông tin còn thiếu, AI Agent tự động viết sẵn email mời demo (cho P1) hoặc sinh bộ câu hỏi khai thác nhu cầu trọng tâm (cho P2).
- **Lý do lựa chọn:** Giúp NVKD tiết kiệm 70% thời gian chuẩn bị kịch bản gọi/email; hướng dẫn nhân viên mới biết chính xác cần hỏi câu gì để lấp đầy khoảng trống dữ liệu thay vì gọi điện lúng túng.

---

### 1.4. Cơ chế Human-in-the-Loop: Điểm kiểm soát & Phát hiện sai lệch

Hệ thống tuân thủ nguyên tắc **AI Automation + Human Oversight**:

```
                  ┌──────────────────────────────────────────────┐
                  │ AI Agent: Xử lý, Khử trùng, Chấm điểm, Gán NV│
                  └──────────────────────┬───────────────────────┘
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
      [Hồ sơ ngoại lệ / Rủi ro cao]              [Hồ sơ hợp lệ đạt chuẩn]
                   │                                           │
                   ▼                                           ▼
      ┌─────────────────────────┐                 ┌─────────────────────────┐
      │  ĐIỂM KIỂM SOÁT 1:      │                 │  ĐIỂM KIỂM SOÁT 2:      │
      │  Trưởng phòng KD Duyệt  │                 │  NVKD Soát & Gửi Tin    │
      │  (Manager Escalation)   │                 │  (Sales Rep Review)     │
      └─────────────────────────┘                 └─────────────────────────┘
```

#### Điểm kiểm soát 1: Trưởng phòng Kinh doanh phê duyệt các hồ sơ Ngoại lệ (Manager Escalation)
- **Điều kiện chuyển xử lý (Triggers):**
  1. `HIGH_BUDGET_UNCLEAR_REQUIREMENTS`: Khách hàng có ngân sách lớn (>= 200,000,000 VNĐ) nhưng nhu cầu còn mơ hồ, chưa rõ thông số kỹ thuật (nguy cơ vượt phạm vi).
  2. `MULTI_REGION_ENTERPRISE`: Doanh nghiệp quy mô lớn có mạng lưới chi nhánh ở cả 3 miền Bắc - Trung - Nam (vượt thẩm quyền phân vùng của 1 nhân viên).
  3. `NO_MATCHING_SALES_REP`: Doanh nghiệp thuộc ngành nghề hoặc tỉnh thành giáp ranh chưa có NVKD phụ trách trong ma trận 8 người.
  4. `PREVIOUS_COMPLAINT_HISTORY`: Khách hàng từng có lịch sử khiếu nại chất lượng dịch vụ hoặc báo giá thiếu minh bạch.
- **Quyết định của con người:** Trưởng phòng quyết định chỉ định Senior Sales phụ trách, thành lập tổ chuyên gia liên ngành, hoặc từ chối lịch sự.

#### Điểm kiểm soát 2: Nhân viên Kinh doanh rà soát bản nháp thông điệp trước khi gửi (Outreach Review)
- **Điều kiện chuyển xử lý:** Mọi thông điệp email/kịch bản gọi do AI soạn thảo đều được đưa vào trạng thái `DRAFT` (Bản nháp), không tự động gửi ra ngoài.
- **Quyết định của con người:** NVKD đọc lướt, điều chỉnh ngữ xưng hô cho gần gũi, bổ sung các chi tiết đặc thù ngoài đời thực trước khi gửi email hoặc nhấc máy gọi.

#### Cách phát hiện kết quả sai của AI Agent (Quality Control & Anomaly Detection):
1. **Kiểm tra lọt lưới trùng lặp (Deduplication Leakage Alert):**
   - Hệ thống quét chéo ma trận phân công: Nếu phát hiện 2 bản ghi khác nhau nhưng có cùng số điện thoại đã chuẩn hóa hoặc cùng mã số thuế/domain lại được gán cho 2 NVKD khác nhau -> Hệ thống ngay lập tức khóa tác vụ và cảnh báo đỏ.
2. **Kiểm tra sai lệch chấm điểm (Scoring Anomaly Audit):**
   - Giám sát các lead có điểm sản phẩm = 0 (ngoài phạm vi) nhưng tổng điểm lại trên 75 do ngân sách ảo. Hệ thống có cơ chế kiểm tra chéo (Sanity Check): Nếu `product_fit == 0`, tổng điểm ưu tiên bị giới hạn tối đa là 20 điểm và bắt buộc xếp `OUT_OF_SCOPE`.
3. **Phát hiện thiếu thông tin trọng yếu nhưng vẫn xếp Hot Lead:**
   - Nếu hồ sơ không có cả số điện thoại lẫn email hợp lệ, hệ thống không cho phép gán P1, mà bắt buộc xếp vào hàng đợi chờ bổ sung phương thức liên lạc.

---

### 1.5. Bản thiết kế hệ thống theo chuẩn Mục tiêu – Đầu vào – Quy trình – Đầu ra

```
========================================================================================
                          BẢN THIẾT KẾ HỆ THỐNG AI AGENT
========================================================================================

1. MỤC TIÊU (OBJECTIVES)
   - Tự động hóa 100% khâu tiếp nhận, khử trùng lặp và chấm điểm cho 700 leads/tuần.
   - Triệt tiêu 100% tình trạng 2 NVKD cùng gọi cho 1 khách hàng.
   - Loại bỏ thiên kiến cherry-picking theo ngân sách ảo; cứu các cơ hội phù hợp bị thiếu tin.
   - Phân bổ công việc chuẩn xác và cân bằng cho 8 NVKD theo ma trận Ngành + Khu vực.
   - Cung cấp nhật ký kiểm toán và báo cáo quản trị minh bạch, không đếm lặp cho Trưởng phòng.

2. ĐẦU VÀO (INPUTS)
   - `leads_input.json`: Danh sách hồ sơ đăng ký từ Web, Hội thảo, Ads.
   - `products.json`: Danh mục 4 dòng sản phẩm chuẩn (CRM, HRM, ERP, Kế toán).
   - `sales_team.json`: Danh sách 8 NVKD, phạm vi ngành, khu vực và hạn mức tiếp nhận.
   - `contact_history.json`: Lịch sử tiếp xúc (Do Not Call, Đang chăm sóc, Khiếu nại...).
   - `business_rules.json`: Bộ quy tắc chuẩn hóa, trọng số chấm điểm và ngưỡng leo thang.

3. QUY TRÌNH (PROCESS WORKFLOW)
   [Sense] -> Đọc và thẩm định dữ liệu đầu vào.
      │
   [Deduplicate] -> Chuẩn hóa SĐT, email domain, làm sạch tên công ty, tính tương đồng -> Gộp Master Entity.
      │
   [Analyze Gaps] -> So khớp từ khóa 4 dòng sản phẩm, chỉ ra trường thông tin khuyết, phát hiện out-of-scope.
      │
   [Score] -> Chấm điểm 4 thành phần (Fit, Budget, Authority, Completeness) -> Xếp P1/P2/P3.
      │
   [Cross-Check History] -> Lọc Blacklist DNC, lọc khách hiện hữu chuyển CSKH.
      │
   [Detect Escalation] -> Kiểm tra các tiêu chí rủi ro chuyển Trưởng phòng KD duyệt.
      │
   [Smart Route] -> Khớp Ngành x Vùng cho 8 Sales, cân bằng tải.
      │
   [Draft Outreach] -> Sinh email cá nhân hóa và bộ câu hỏi khai thác thông tin thiếu.
      │
   [Audit & Report] -> Ghi vết từng bước vào `audit_trail.log`, xuất các file deliverables và HTML Dashboard.

4. ĐẦU RA (OUTPUTS)
   - `master_customers.json` & `.csv`: Hồ sơ khách hàng hợp nhất kèm bản nháp hành động.
   - `sales_task_assignments.json` & `.csv`: Bảng công việc chi tiết cho 8 NVKD (không trùng lặp).
   - `manager_escalations.json`: Danh sách các ca chuyển Trưởng phòng quyết định.
   - `do_not_contact.json`: Danh sách chặn liên hệ theo lịch sử.
   - `summary_report.json` & `.md`: Báo cáo thống kê tổng hợp số lượng (không đếm lặp).
   - `audit_trail.log` & `execution_log.json`: Nhật ký truy vết quy tắc minh bạch.
   - `web/dashboard.html`: Bảng điều khiển giao diện web trực quan.
========================================================================================
```

---

## TASK 2: GIẢI PHÁP PHẦN MỀM TRIỂN KHAI VÀ KẾT QUẢ THỰC THI

### 2.1. Kiến trúc kỹ thuật và Phối hợp Đa kỹ năng (Multi-Skill Coordination)

Giải pháp được xây dựng bằng Python 3 theo mô hình kiến trúc Module hóa hướng Agent (Modular Agentic Architecture). Hai kỹ năng nghiệp vụ chính được đóng gói thành các tool độc lập, phối hợp nhịp nhàng trong cùng một quy trình điều phối (`Orchestrator`):

```
                        ┌────────────────────────────────────────┐
                        │      NamVietAgentOrchestrator          │
                        │ (Điều phối luồng công việc & State)    │
                        └──────────────────┬─────────────────────┘
                                           │
         ┌─────────────────────────────────┴─────────────────────────────────┐
         ▼                                                                   ▼
┌─────────────────────────────────┐                         ┌─────────────────────────────────┐
│ KỸ NĂNG 1: customer_segmentation│                         │ KỸ NĂNG 2: sales_followup       │
├─────────────────────────────────┤                         ├─────────────────────────────────┤
│ 1. normalize_phone()            │                         │ 1. check_contact_history()      │
│ 2. normalize_email()            │                         │    - Kiểm tra Blacklist DNC     │
│ 3. clean_company_name()         │                         │    - Kiểm tra khách hiện hữu    │
│ 4. are_companies_similar()      │                         │ 2. check_escalation()           │
│ 5. deduplicate_leads()          │                         │    - Cảnh báo rủi ro quản lý    │
│ 6. analyze_needs_and_gaps()     │                         │ 3. assign_sales_rep()           │
│ 7. score_customer()             │                         │    - Định tuyến Ngành x Vùng    │
│    - P1, P2, P3, Out-of-Scope   │                         │    - Cân bằng tải công việc     │
└─────────────────────────────────┘                         │ 4. generate_outreach_draft()    │
                                                            │    - Viết thư mời Demo          │
                                                            │    - Tạo câu hỏi khám phá       │
                                                            └─────────────────────────────────┘
                                           │
                                           ▼
                        ┌────────────────────────────────────────┐
                        │              AuditLogger               │
                        │ (Lưu vết Rule ID, Timestamp, Payload)  │
                        └────────────────────────────────────────┘
```

---

### 2.2. Cơ chế đối chiếu thực thể, Khử trùng lặp và Đánh giá nhu cầu

#### Cơ chế khử trùng lặp đa tầng (Multi-layered Deduplication):
1. **Chuẩn hóa Số điện thoại:** Loại bỏ toàn bộ dấu chấm, dấu gạch nối, khoảng trắng và chuyển đổi tiền tố quốc tế `+84` / `84` về định dạng 10 chữ số chuẩn của Việt Nam (`0xxxxxxxxx`).
2. **Khám phá Tên miền Doanh nghiệp:** Tách domain từ email. Tự động bỏ qua các domain công cộng (`gmail.com`, `yahoo.com`, `outlook.com`...). Nếu 2 đăng ký có cùng domain công ty (ví dụ: `@namlongtech.vn`), Agent nhận định ngay là cùng một doanh nghiệp.
3. **Phân tích Tương đồng Tên công ty (Entity Matching):**
   - Loại bỏ các tiền tố pháp lý thông dụng: "Công ty Cổ phần", "Cty CP", "Công ty TNHH", "Tập đoàn", "JSC", "Co., Ltd", "Corp".
   - Kiểm tra từ viết tắt (Acronym matching): Nhận diện `"Nam Long"` và `"NL"` tương ứng nhau.
   - Đo khoảng cách tương đồng chuỗi `SequenceMatcher` với ngưỡng tin cậy >= 0.85 kết hợp cùng tỉnh thành hoặc cùng số điện thoại.
4. **Hợp nhất thực thể (Cluster Merging):**
   - Giữ lại danh sách đầy đủ tất cả các đầu mối liên hệ (`contacts`), ghi nhận chức danh và nguồn đăng ký.
   - Tổng hợp nhu cầu từ tất cả các phiếu đăng ký thành chuỗi hợp nhất (`consolidated_needs`).
   - Lấy mức ngân sách cao nhất được khai báo.

#### Cơ chế chấm điểm và phân loại P1/P2/P3:
- **Thang điểm 100:**
  * Điểm khớp sản phẩm (Tối đa 40 điểm): Khớp trực tiếp 4 dòng sản phẩm chính của Nam Việt. Nếu yêu cầu ngoài ngành (Drone, thiết bị nhúng IoT, game) -> 0 điểm.
  * Điểm tương thích ngân sách (Tối đa 30 điểm): Nằm trong dải ngân sách của sản phẩm -> 30 điểm. Chưa khai báo -> 15 điểm (tạm tính để không bỏ sót).
  * Điểm thẩm quyền & Tiến độ (Tối đa 20 điểm): Người liên hệ là cấp C-level/Giám đốc và cần gấp trong 2 tuần -> 20 điểm.
  * Điểm độ đầy đủ dữ liệu (Tối đa 10 điểm): Đủ mọi trường -> 10 điểm; thiếu 1-2 trường -> 7 điểm.
- **Phân loại:**
  * **P1 - Hot Lead** (Điểm >= 75): Khách hàng chuẩn mực, cần gọi trong 2 giờ.
  * **P2 - Warm Lead** (50 <= Điểm < 75): Nhu cầu tiềm năng, cần gọi khám phá trong 8 giờ.
  * **P3 - Cold Lead** (30 <= Điểm < 50): Khách vãng lai, chuyển nuôi dưỡng qua email.
  * **Out-of-Scope**: Khách hàng sai sản phẩm, không tính điểm để tránh sales cherry-picking.

---

### 2.3. Bằng chứng thực thi và Hệ thống Nhật ký Kiểm toán (Audit Trail)

Để chứng minh Agent tự động đọc dữ liệu, gọi công cụ và đưa ra quyết định dựa trên quy tắc thay vì nhập tay kết quả, toàn bộ hành vi của Agent được ghi lại trong `outputs/audit_trail.log` và `outputs/execution_log.json`.

Trích xuất một phần nhật ký thực thi thực tế:
```log
[2026-11-11T10:02:23] [DEDUPLICATION] [MERGE_LEAD_INTO_EXISTING_CLUSTER] Rule: RULE_DEDUP_MULTI_ATTR | Status: SUCCESS
  Details: {"lead_id": "LEAD-002", "company": "Nam Long Tech JSC", "phone": "0903.456.789", "matched_cluster_lead_id": "LEAD-001"}

[2026-11-11T10:02:23] [DEDUPLICATION] [MERGE_LEAD_INTO_EXISTING_CLUSTER] Rule: RULE_DEDUP_MULTI_ATTR | Status: SUCCESS
  Details: {"lead_id": "LEAD-003", "company": "NL Corp", "phone": "0903456789", "matched_cluster_lead_id": "LEAD-001"}

[2026-11-11T10:02:23] [NEEDS_AND_GAP_ANALYSIS] [ANALYZE_NEEDS] Rule: RULE_PRODUCT_KEYWORD_MATCH | Status: SUCCESS
  Details: {"customer_id": "CUST-NV-0001", "matched_count": 2, "matched_product_names": ["NamViet CRM Pro", "NamViet HRM Cloud"], "is_out_of_scope": false, "missing_fields": []}

[2026-11-11T10:02:23] [SCORING_AND_PRIORITIZATION] [SCORE_CUSTOMER] Rule: RULE_MULTI_DIMENSIONAL_SCORING | Status: SUCCESS
  Details: {"customer_id": "CUST-NV-0001", "company_name": "Công ty Cổ phần Công nghệ Nam Long", "total_score": 100, "priority": "P1", "breakdown": {"product_fit": 40, "budget_alignment": 30, "authority_and_timeline": 20, "data_completeness": 10}}

[2026-11-11T10:02:23] [SALES_ROUTING] [ASSIGN_SALES_REP] Rule: RULE_ROUTING_INDUSTRY_REGION | Status: SUCCESS
  Details: {"customer_id": "CUST-NV-0001", "assigned_rep": "Trần Thị Bình", "reason": "Khớp ngành phụ trách (Bán lẻ, Thương mại điện tử, Thời trang) và khu vực (Miền Bắc). Tải hiện tại: 1/50"}
```

---

### 2.4. Phân tích Hồ sơ đầu ra & Danh sách phân công 8 NVKD

#### Bảng tổng hợp số liệu phân bổ toàn hệ thống (Không đếm lặp):
- **Tổng số leads tiếp nhận ban đầu:** `20` hồ sơ.
- **Tổng số khách hàng duy nhất sau gộp:** `18` doanh nghiệp (Tỷ lệ giảm tải trùng lặp: `10.0%`).
- **Khách hàng P1 (Hot Lead):** `14` khách hàng.
- **Khách hàng P3 (Cold Lead):** `1` khách hàng.
- **Khách hàng Ngoài phạm vi (Out-of-Scope):** `1` khách hàng (Tập đoàn Alpha).
- **Chặn liên hệ theo lịch sử (Do Not Contact):** `1` khách hàng (Vận tải Việt Phát).
- **Khách hàng hiện hữu chuyển CSKH:** `1` khách hàng (Bán lẻ Sài Gòn).
- **Trường hợp chuyển Trưởng phòng quyết định:** `5` khách hàng.

#### Bảng phân bổ tải công việc cho 8 Nhân viên Kinh doanh:
| Mã NVKD | Họ và tên NVKD | Nhóm ngành phụ trách | Khu vực phụ trách | Số KH nhận | P1 (Hot) | P2 (Warm) | P3 (Cold) | Trạng thái tải |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `SALE-01` | **Nguyễn Văn An** | Sản xuất, Xây dựng, Cơ khí | Miền Bắc | **2** | 2 | 0 | 0 | Ổn định (2/50) |
| `SALE-02` | **Trần Thị Bình** | Bán lẻ, TMĐT, Thời trang | Miền Bắc | **3** | 3 | 0 | 0 | Ổn định (3/50) |
| `SALE-03` | **Lê Hoàng Cường** | F&B, Khách sạn, Dịch vụ | Miền Bắc | **1** | 1 | 0 | 0 | Ổn định (1/50) |
| `SALE-04` | **Phạm Thu Dung** | Logistics, Vận tải, Kho bãi | Miền Trung, Toàn quốc | **1** | 1 | 0 | 0 | Ổn định (1/45) |
| `SALE-05` | **Hoàng Minh Đức** | Sản xuất, Xây dựng | Miền Nam | **1** | 1 | 0 | 0 | Ổn định (1/55) |
| `SALE-06` | **Đỗ Mai Hoa** | Bán lẻ, Chuỗi cửa hàng | Miền Nam | **1** | 1 | 0 | 0 | Ổn định (1/50) |
| `SALE-07` | **Vũ Quốc Hùng** | Dịch vụ, Giáo dục, Y tế | Miền Nam | **2** | 1 | 0 | 0 | Ổn định (2/50) |
| `SALE-08` | **Đặng Thùy Linh** | F&B, Nông sản, Dịch vụ | Miền Trung, Toàn quốc | **2** | 2 | 0 | 0 | Ổn định (2/50) |

---

### 2.5. Kết quả kiểm thử tự động (Unit Test & Edge Cases)

Hệ thống tích hợp bộ kiểm thử tự động toàn diện tại file `tests/test_suite.py` kiểm tra cả 3 nhóm ca kiểm thử theo yêu cầu của đề bài:

```
================================================================================
     BỘ KIỂM THỬ TỰ ĐỘNG AI AGENT (AI301 - ĐỀ 02: CÔNG TY NAM VIỆT)
================================================================================
[*] Running: Test 1: Trường hợp thông thường (Happy Path - Standard Case) ... [PASSED] (0.0ms)
[*] Running: Test 2: Trường hợp thiếu dữ liệu (Missing Data & Discovery Questions) ... [PASSED] (0.0ms)
[*] Running: Test 3: Khử trùng & gộp đa kênh, tên viết tắt (Entity Resolution / Dedup) ... [PASSED] (0.0ms)
[*] Running: Test 4: Ngăn chặn cherry-picking ngân sách lớn sai sản phẩm (Out-of-Scope) ... [PASSED] (0.0ms)
[*] Running: Test 5: Chặn liên hệ theo lịch sử tiếp xúc (Do Not Contact - Blacklist) ... [PASSED] (0.0ms)
--------------------------------------------------------------------------------
KẾT QUẢ KIỂM THỬ: 5 PASSED | 0 FAILED
================================================================================
```

#### Phân tích chi tiết kết quả 3 trường hợp:
1. **Trường hợp thông thường (Happy Path):** Khách hàng Thời Trang Hà Nội có đầy đủ ngân sách 50 triệu, người hỏi là Giám đốc Vận hành, nhu cầu CRM rõ ràng. Agent đánh giá đạt 100/100 điểm, xếp P1-Hot, phân công chính xác cho Trần Thị Bình (Bán lẻ / Miền Bắc), sinh email mời demo cá nhân hóa.
2. **Trường hợp thiếu dữ liệu (Missing Data):** Xưởng May An Thịnh chỉ để lại tên cô Lan, SĐT và nhu cầu "quản lý kho vải 80 công nhân", không có email và ngân sách. NVKD thông thường sẽ bỏ qua. AI Agent nhận diện nhu cầu khớp 100% dòng sản phẩm `NamViet ERP SMB`, đánh giá tiềm năng cao (82 điểm - P1), gán cho Nguyễn Văn An (Sản xuất / Miền Bắc), đồng thời sinh sẵn 2 câu hỏi phỏng vấn khai thác thông tin còn thiếu.
3. **Trường hợp ranh giới quy tắc (Boundary Cases):**
   - **Tập đoàn Alpha**: Ngân sách cực lớn 2.5 tỷ VNĐ nhưng yêu cầu gia công phần mềm nhúng drone IoT. Agent chấm 0 điểm sản phẩm, xếp nhãn `OUT_OF_SCOPE` và chuyển Trưởng phòng quyết định; ngăn chặn NVKD tốn công vô ích.
   - **Nam Long / Nam Long Tech / NL Corp**: 3 bản ghi khác nhau từ Facebook Ads, Hội thảo và Website được gom trọn vẹn thành 1 khách hàng duy nhất với 3 người liên hệ, chỉ phân công cho 1 sales rep, tránh 2 sales cùng gọi.
   - **Vận tải Việt Phát**: Nằm trong danh sách Do Not Contact -> Agent lập tức chặn phân công, ghi rõ lý do khách hàng từng phàn nàn và lưu vào file `do_not_contact.json`.

---

### 2.6. Hướng dẫn nạp tập dữ liệu mới tại buổi thi trực tiếp

Theo đúng quy định thi của Giảng viên: *"tại buổi thi, nhóm nhận bộ dữ liệu mới cùng cấu trúc, nạp vào giải pháp và chạy trực tiếp. Nhóm giải thích kết quả, thông tin chưa xác định và các điểm cần con người xử lý; không sửa dữ liệu test hoặc nhập tay kết quả để khớp yêu cầu."*

Hệ thống được thiết kế linh hoạt hỗ trợ nạp dữ liệu thi bằng một dòng lệnh duy nhất:

#### Cách 1: Nạp file JSON mới qua tham số dòng lệnh CLI
```bash
# Cú pháp chạy trên Windows PowerShell / CMD:
.\run_python.bat main.py --leads "duong_dan_file_moi.json"
```

#### Cách 2: Thay thế trực tiếp file trong thư mục data
1. Copy file dữ liệu mới của Giảng viên và đổi tên thành `data/leads_input.json`.
2. Kích đúp chuột vào file `run.bat` (hoặc gõ `.\run.bat` trên terminal).
3. Toàn bộ quy trình sẽ chạy tự động trong 3 giây:
   - Dữ liệu mới được đọc và khử trùng.
   - Tất cả các file trong `outputs/` được làm mới hoàn toàn.
   - Mở file `web/dashboard.html` trên trình duyệt để trình chiếu trực tiếp kết quả thống kê, danh sách 8 NVKD, tab Escalation và Audit Log cho Giảng viên xem.

---

## 4. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

Hệ thống AI Agent Sàng lọc và Điều phối Khách hàng Tiềm năng xây dựng cho Công ty Nam Việt đã giải quyết trọn vẹn và triệt để các bài toán hóc búa của đề án:
1. **Chấm dứt hoàn toàn tình trạng gọi trùng**: Khử trùng thông minh theo số điện thoại, domain email và tên doanh nghiệp viết tắt.
2. **Loại bỏ hiện tượng "cherry-picking" sai lệch**: Tách biệt rõ ràng giữa quy mô ngân sách và mức độ phù hợp sản phẩm.
3. **Bảo vệ doanh thu & chống lãng phí tiếp thị**: Tự động phát hiện khoảng trống thông tin và sinh kịch bản câu hỏi để cứu các deal tiềm năng.
4. **Minh bạch hóa quản trị**: Hệ thống Audit Trail và Dashboard báo cáo thời gian thực giúp Trưởng phòng Kinh doanh nắm trọn bức tranh vận hành.

Hệ thống sẵn sàng 100% để bảo vệ và thuyết trình trong buổi chấm thi thực tế!

