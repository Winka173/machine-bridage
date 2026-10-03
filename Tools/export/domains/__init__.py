"""The domain files: one module each, built in this order.

A domain module defines
    FILE_ID = "05_che_do_kinh_te"          # the xlsx / csv / md name (spec 1)
    TITLE = "Chế độ và kinh tế"            # Vietnamese title (Muc_luc_file)
    DESC = "..."                            # one line
    def build(ctx): ...                     # book = ctx.book(FILE_ID, TITLE, DESC); book.sheet(...); row.set / row.flatten
To add a file: write domains/dNN_<name>.py, add its module name below, and delete its claims in domains/_pending.py
(the coverage test then fails on every leaf the new module does not export).
"""

DOMAINS = [
    "d01_vu_khi_dan",
    "d02_phuong_tien",
    "d03_boss",
    "d04_can_cu_thap",
    "d05_che_do_kinh_te",
    "d06_ai",
    "d07_chien_dich_cot_truyen",
    "d08_ban_do",
    "d09_hieu_ung_am_thanh",
    "d10_model_tai_san",
    "d11_meta_giao_dien",
    "d12_he_thong_trang_thai",
    "d13_tham_chieu_nguon",  # pass 10 (spec 12): also adds <name>_tham_chieu / _so_sanh_that to 01-11
]

# Every file of the spec (1 and 12.3), for Muc_luc_file: the ones not built yet are listed as not exported.
PLANNED = {
    "01_vu_khi_dan": "Vũ khí và đạn",
    "02_phuong_tien": "Phương tiện",
    "03_boss": "Boss",
    "04_can_cu_thap": "Căn cứ và tháp",
    "05_che_do_kinh_te": "Chế độ và kinh tế",
    "06_ai": "AI",
    "07_chien_dich_cot_truyen": "Chiến dịch và cốt truyện",
    "08_ban_do": "Bản đồ",
    "09_hieu_ung_am_thanh": "Hiệu ứng và âm thanh",
    "10_model_tai_san": "Model và tài sản",
    "11_meta_giao_dien": "Meta và giao diện",
    "12_he_thong_trang_thai": "Hệ thống và trạng thái",
    "13_tham_chieu_nguon": "Tham chiếu ngoài đời và game (nguồn)",
}
