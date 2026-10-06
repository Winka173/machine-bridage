# 06/10 owner answers to balance v3 open decisions (verbatim)



<pasted_content id="e0cc">
spawn_bastion: giữ nguyên. Không có entity nào đủ rõ để áp nhóm “fortress-style tower”, nên §22 phần đó coi như không có đối tượng áp dụng ở pass này. Không suy diễn từ tên/model.

supply_truck: hoàn tác +15% HP nếu đúng là CP 0/event-spawned và không phải unit mua thông thường. Rule cheap/mid chỉ nên áp cho unit tham gia economy/roster mua bằng CP. CP=0 scripted/free/event unit không được tự động buff chỉ vì nằm trong support class. Nếu có player-buyable path riêng thì audit path đó trước; nếu không, KEEP original HP.

cp_relay: giữ rule cũ đã áp. Không cộng thêm utility-tower +15%. Mỗi entity chỉ nhận một classification balance rule, tránh double buff.

Earth Borer: chưa nerf boss. Data hiện cho thấy Earth Borer có burrow hit 350 damage, radius 6 m, stun 3 s, warning 2 s, ngoài hai borer_cannon; bản thân boss stat không cần đổi chỉ vì regression này. 02_boss Việc survival giảm 2/3 → 1/3 trong khi boss unchanged rất có khả năng đến từ composition/economy side effect: cheap units vừa tăng CP nên cùng ngân sách có ít thân xe hơn, hoặc formation/pathing khiến nhiều unit cùng dính burrow.
</pasted_content id="e0cc">

