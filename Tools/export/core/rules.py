"""Khong_xuat rules shared by every domain (spec 8 and 3.3): what is never exported, with the reason.

A domain adds its own with ctx.exclude(source_glob, pattern, reason). Security (spec 8, verbatim): "KHÔNG xuất: khóa API,
mật khẩu keystore, thông tin tài khoản Play Console, token, dữ liệu cá nhân người chơi, đường dẫn tuyệt đối máy cá nhân."
"""
from __future__ import annotations

# (source glob, leaf pattern, reason)
SHARED = [
    # secrets and personal data: none are in the scanned sources today; these patterns keep any that appear out
    ("*", "**.*password*", "bảo mật: mật khẩu (spec 8)"),
    ("*", "**.*keystore*", "bảo mật: keystore (spec 8)"),
    ("*", "**.*apikey*", "bảo mật: khóa API (spec 8)"),
    ("*", "**.*token", "bảo mật: token (spec 8)"),
    ("*", "**.*secret*", "bảo mật: bí mật (spec 8)"),
    # Unity renderer and device settings: no gameplay field (the render pipeline, Vulkan filters, the scene layout)
    ("Assets/Settings/*.asset", "**", "cấu hình render URP (không có trường lối chơi)"),
    ("Assets/MachineBrigade/Settings/VulkanDeviceFilters.asset", "**", "bộ lọc thiết bị Vulkan (không có trường lối chơi)"),
    ("Assets/MachineBrigade/Scenes/*.unity", "**",
     "cảnh Unity: chỉ bố cục khởi động; lối chơi đọc từ dữ liệu lúc chạy (SceneBuilder dựng cảnh)"),
    # tool-only files: the Python requirements of the music tool
    ("Tools/export/pack2/*.csv", "**", "danh sách việc của công cụ chuyển số vào dữ liệu (không phải dữ liệu game)"),
    ("Tools/music/requirements.txt", "**", "danh sách gói Python của công cụ nhạc (không phải dữ liệu game)"),
    # Unity YAML bookkeeping of every document (object ids, hide flags): not data
    ("*.asset", "docs[*]._class", "mã lớp Unity của tài liệu YAML (siêu dữ liệu)"),
    ("*.asset", "docs[*]._file_id", "mã đối tượng Unity (siêu dữ liệu)"),
    ("*.asset", "docs[*].*.m_ObjectHideFlags", "cờ ẩn của Unity (siêu dữ liệu)"),
    ("*.asset", "docs[*].*.m_CorrespondingSourceObject", "liên kết prefab của Unity (siêu dữ liệu)"),
    ("*.asset", "docs[*].*.m_PrefabInstance", "liên kết prefab của Unity (siêu dữ liệu)"),
    ("*.asset", "docs[*].*.m_PrefabAsset", "liên kết prefab của Unity (siêu dữ liệu)"),
    ("*.asset", "docs[*].*.m_GameObject", "liên kết GameObject của Unity (siêu dữ liệu)"),
    ("*.asset", "docs[*].*.m_Script", "guid script của Unity (siêu dữ liệu)"),
    ("*.asset", "docs[*].*.m_EditorHideFlags", "cờ editor của Unity (siêu dữ liệu)"),
    ("*.asset", "docs[*].*.m_EditorClassIdentifier", "định danh editor của Unity (siêu dữ liệu)"),
]
