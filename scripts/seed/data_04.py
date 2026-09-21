"""Recipes for categories 13-16 (chè, bánh ngọt, đồ uống, món ăn kèm)."""

RECIPES = [
    dict(
        title="Chè chuối chưng",
        desc="Chuối sứ chưng đường thốt nốt, nước cốt dừa béo và bột báng dai mềm, ngọt thanh dễ ăn.",
        prep=20,
        cook=40,
        serv=5,
        lvl=1,
        nut=(360, 3, 62, 12, 3, 60),
        ing="""
6 quả | Chuối sứ | chín vừa, thái khoanh
80 g | Bột báng | ngâm nở
500 ml | Nước cốt dừa |
100 g | Đường cát |
50 g | Đường thốt nốt |
1/2 muỗng cà phê | Muối |
500 ml | Nước lọc |
2 lá | Lá dứa | buộc lại
1 muỗng canh | Bột năng | làm sánh
50 g | Đậu phộng rang | giã nhỏ
30 g | Dừa nạo sợi |
1 muỗng cà phê | Vani |
""",
        steps="""
Nấu bột báng | Luộc bột báng với nước và lá dứa đến khi trong, vớt ra. | 15
Chưng chuối | Trộn chuối với đường thốt nốt, chưng lửa nhỏ 10 phút đến khi mềm. | 12
Nấu nước chè | Đun nước với đường cát, muối, lá dứa 10 phút. | 10
Làm sánh | Cho nước cốt dừa, bột năng hòa nước, khuấy đều đến khi hơi sánh. | 8
Kết hợp | Cho chuối và bột báng vào nồi, khuấy nhẹ, tắt bếp. | 3
Thưởng thức | Múc chè ra chén, rắc đậu phộng, ăn nóng hoặc lạnh. | 2
""",
    ),
    dict(
        title="Chè đậu xanh",
        desc="Chè đậu xanh nấu nhừ ngọt thanh mùi lá dứa, dùng nóng hay ướp đá đều mát dịu.",
        prep=20,
        cook=45,
        serv=5,
        lvl=1,
        nut=(280, 8, 55, 3, 5, 40),
        ing="""
200 g | Đậu xanh cà | ngâm 2 giờ
1.2 lít | Nước lọc |
150 g | Đường phèn |
2 lá | Lá dứa | buộc nút
1 lá | Lá dứa | giã lấy nước, tạo màu
1 muỗng canh | Bột năng | hòa nước
1/4 muỗng cà phê | Muối |
100 ml | Nước cốt dừa |
30 g | Dừa nạo sợi |
1 muỗng canh | Đậu phộng rang |
100 g | Đá viên | dùng lạnh
1/2 muỗng cà phê | Vani |
""",
        steps="""
Ngâm đậu | Ngâm đậu xanh nở rồi rửa sạch, để ráo. | 120
Nấu đậu | Nấu đậu với nước và lá dứa lửa nhỏ 30 phút đến khi đậu nở nhuyễn. | 30
Nêm chè | Thêm đường phèn, muối, khuấy đều cho đường tan. | 5
Làm sánh | Cho bột năng hòa nước vào, khuấy đến khi chè sánh nhẹ. | 5
Hoàn thiện | Thêm nước cốt dừa, vani, tắt bếp. | 3
Thưởng thức | Múc chè ra chén, rắc dừa, đậu phộng, thêm đá nếu dùng lạnh. | 2
""",
    ),
    dict(
        title="Chè đậu đen",
        desc="Đậu đen nấu mềm với đường phèn, nước cốt dừa và lá dứa, món chè giải nhiệt dân dã.",
        prep=20,
        cook=60,
        serv=5,
        lvl=1,
        nut=(300, 10, 52, 5, 6, 50),
        ing="""
200 g | Đậu đen | ngâm 6 giờ
1.5 lít | Nước lọc |
150 g | Đường phèn |
1/2 muỗng cà phê | Muối |
3 lá | Lá dứa | buộc nút
200 ml | Nước cốt dừa |
2 muỗng canh | Bột năng |
50 g | Dừa nạo | rang vàng
1 miếng | Gừng | đập dập, tùy chọn
30 g | Đậu phộng rang |
1 muỗng cà phê | Vani |
100 g | Đá viên |
""",
        steps="""
Ngâm đậu | Ngâm đậu đen ít nhất 6 giờ. | 360
Hầm đậu | Đun đậu với nước và lá dứa lửa nhỏ 45 phút đến khi mềm. | 45
Nêm ngọt | Cho đường phèn, muối, gừng vào nấu 10 phút. | 10
Chuẩn bị nước cốt | Hòa bột năng với nước cốt dừa, đun nhỏ lửa cho sánh nhẹ. | 5
Thưởng thức | Múc chè ra chén, rưới nước cốt dừa, rắc đậu phộng, dùng nóng hay lạnh. | 3
""",
    ),
    dict(
        title="Chè khúc bạch",
        desc="Khối khúc bạch mềm mịn vị sữa hạnh nhân, ăn cùng nhãn, vải và siro, món tráng miệng mát lạnh.",
        prep=30,
        cook=15,
        serv=6,
        lvl=2,
        nut=(230, 6, 32, 9, 1, 60),
        ing="""
300 ml | Kem tươi |
300 ml | Sữa tươi |
40 g | Đường |
15 g | Bột gelatin |
1 muỗng cà phê | Tinh chất hạnh nhân |
100 g | Hạt é | hoặc hạt chia
200 g | Nhãn đóng hộp |
200 g | Vải đóng hộp |
100 g | Hạnh nhân lát | rang
200 ml | Siro vải |
100 g | Đá bào |
1 muỗng canh | Nước cốt chanh |
""",
        steps="""
Ngâm gelatin | Ngâm gelatin với nước lạnh 5 phút cho nở mềm. | 5
Nấu hỗn hợp | Đun sữa, kem, đường đến khi nóng (không sôi), cho gelatin và tinh chất hạnh nhân. | 8
Đổ khuôn | Rót hỗn hợp vào khuôn, để nguội và làm lạnh 4 giờ. | 240
Chuẩn bị topping | Rửa nhãn, vải, rang hạnh nhân, ngâm hạt é. | 10
Cắt khúc bạch | Cắt khúc bạch thành khối nhỏ vừa ăn. | 5
Thưởng thức | Cho khúc bạch, nhãn, vải, hạt é vào ly, rưới siro và đá bào. | 3
""",
    ),
    dict(
        title="Bánh rán ngọt",
        desc="Vỏ bánh giòn, bên trong dẻo, nhân đậu xanh thơm bùi, lăn mè trắng thơm ngọt.",
        prep=60,
        cook=25,
        serv=8,
        lvl=3,
        nut=(320, 6, 50, 11, 3, 40),
        ing="""
300 g | Bột nếp |
100 g | Bột gạo |
200 g | Đường | phần nhân và nước
250 ml | Nước lọc ấm |
150 g | Đậu xanh cà | hấp chín, nghiền
30 g | Bơ | trộn nhân
30 g | Vừng (mè) trắng |
1 muỗng cà phê | Vani |
500 ml | Dầu ăn | chiên ngập
1/4 muỗng cà phê | Muối |
50 g | Dừa nạo |
1 muỗng canh | Nước cốt dừa |
""",
        steps="""
Làm nhân | Trộn đậu xanh nghiền với đường, bơ, vani; vo tròn, để nguội. | 15
Nhào bột | Trộn bột nếp, bột gạo, đường, muối, nước ấm nhào thành khối dẻo mịn. | 10
Nghỉ bột | Ủ bột 30 phút cho nở. | 30
Tạo bánh | Chia bột, dàn mỏng, cho nhân vào, vo kín, lăn mè. | 15
Chiên bánh | Chiên lửa vừa 8-10 phút đến khi vàng đều. | 10
Thưởng thức | Vớt ráo dầu, ăn nóng hoặc nguội đều ngon. | 3
""",
    ),
    dict(
        title="Bánh flan caramel",
        desc="Bánh flan mịn lạnh béo sữa trứng, phủ lớp caramel đắng nhẹ, tráng miệng kinh điển.",
        prep=20,
        cook=45,
        serv=6,
        lvl=2,
        nut=(210, 6, 30, 7, 0, 90),
        ing="""
5 quả | Trứng gà |
500 ml | Sữa tươi không đường |
100 g | Đường cát | làm sốt trứng sữa
80 g | Đường cát | làm caramel
30 ml | Nước lọc | làm caramel
1 muỗng cà phê | Vani |
1 nhúm | Muối |
100 ml | Kem tươi |
1 muỗng canh | Cà phê hòa tan | tùy chọn
100 ml | Sữa đặc | tăng độ béo ngọt
500 ml | Nước sôi | hấp cách thủy
1 muỗng canh | Rượu rum | khử mùi trứng, tùy chọn
""",
        steps="""
Làm caramel | Đun đường với nước đến khi vàng nâu, đổ vào đáy khuôn. | 8
Trộn kem trứng | Đánh trứng với đường, thêm sữa ấm, vani, muối, khuấy nhẹ tay. | 8
Lọc hỗn hợp | Lọc hỗn hợp qua rây để bánh mịn. | 3
Đổ khuôn | Rót vào khuôn có caramel, đậy giấy bạc. | 3
Hấp cách thủy | Hấp lửa nhỏ 30-35 phút đến khi bánh đông. | 35
Làm lạnh | Để nguội, cho vào tủ mát 3 giờ rồi úp ra đĩa. | 180
""",
    ),
    dict(
        title="Bánh đậu xanh Hải Dương",
        desc="Bánh đậu xanh mềm mịn, tan trong miệng với hương thơm bùi ngọt của đậu xanh và dầu ăn.",
        prep=60,
        cook=50,
        serv=10,
        lvl=3,
        nut=(210, 6, 30, 7, 2, 20),
        ing="""
300 g | Đậu xanh đã bóc vỏ |
200 g | Đường cát |
100 ml | Dầu ăn |
50 g | Mỡ heo | hoặc bơ thực vật
2 muỗng canh | Bột nếp | xào chín
1/2 muỗng cà phê | Hương vani |
1 nhúm | Muối |
1 muỗng canh | Nước cốt chanh |
50 ml | Nước lọc |
20 g | Vừng (mè) rang | rắc mặt
1 muỗng canh | Bột gạo rang | chống dính khi nén khuôn
1 muỗng cà phê | Nước hoa bưởi | tạo hương, tùy chọn
""",
        steps="""
Hấp đậu | Ngâm đậu xanh 4 giờ, hấp chín mềm. | 30
Nghiền đậu | Nghiền đậu thật mịn, rây lại cho sợi nhỏ. | 10
Thắng đường | Đun đường với nước, chanh đến khi tan sánh nhẹ. | 8
Xào bột | Cho đậu vào chảo, đổ đường vào, thêm dầu ăn từng ít một, đảo liên tục lửa nhỏ. | 30
Nén khuôn | Khi bột mịn, ráo, cho vào khuôn, nén chặt, để nguội. | 10
Hoàn thiện | Tháo khuôn, gói giấy bóng, để bánh nghỉ 1 ngày. | 5
""",
    ),
    dict(
        title="Bánh da lợn",
        desc="Bánh nhiều lớp xanh vàng xen kẽ, dẻo mềm thơm mùi lá dứa và nước cốt dừa, nhân đậu xanh.",
        prep=40,
        cook=60,
        serv=8,
        lvl=3,
        nut=(250, 3, 48, 6, 2, 30),
        ing="""
200 g | Bột năng |
100 g | Bột gạo |
50 g | Bột đậu xanh |
350 ml | Nước cốt dừa |
250 g | Đường |
500 ml | Nước lọc |
150 g | Đậu xanh cà | hấp chín, nghiền
5 lá | Lá dứa | xay lấy nước
1/4 muỗng cà phê | Muối |
1 muỗng canh | Dầu ăn |
1 muỗng cà phê | Vani |
2 muỗng canh | Dừa nạo | rắc mặt
""",
        steps="""
Pha bột | Trộn các loại bột với đường, muối, nước và nước cốt dừa. | 10
Chia màu | Chia bột làm hai phần, một phần trộn nước lá dứa, một phần trộn đậu xanh. | 10
Hấp lớp đầu | Đổ một lớp bột vào khuôn, hấp 5 phút cho se mặt. | 6
Xếp lớp | Đổ lần lượt lớp bột màu xanh và vàng, hấp mỗi lớp 5 phút. | 45
Làm nguội | Để bánh nguội hoàn toàn rồi cắt miếng. | 60
""",
    ),
    dict(
        title="Bánh bò hấp",
        desc="Bánh bò hấp nở xốp có tổ ong, vị ngọt nhẹ nước cốt dừa, màu xanh lá dứa bắt mắt.",
        prep=40,
        cook=25,
        serv=8,
        lvl=3,
        nut=(180, 2, 34, 4, 1, 40),
        ing="""
200 g | Bột gạo |
50 g | Bột năng |
150 g | Đường |
300 ml | Nước cốt dừa |
150 ml | Nước lá dứa |
1 muỗng cà phê | Men nở |
1 muỗng cà phê | Bột nở |
1/4 muỗng cà phê | Muối |
1 muỗng canh | Dầu ăn |
1 muỗng cà phê | Vani |
2 muỗng canh | Sữa tươi | tăng độ mềm
50 g | Dừa nạo | rắc mặt
""",
        steps="""
Làm men | Hòa men nở với chút nước ấm và đường, để 10 phút. | 10
Trộn bột | Trộn bột gạo, bột năng, đường, muối, nước cốt dừa, nước lá dứa và men. | 10
Ủ bột | Đậy kín, ủ 2 giờ cho bột dậy nở. | 120
Thêm bột nở | Thêm bột nở và dầu ăn, khuấy đều. | 3
Hấp bánh | Rót bột vào khuôn, hấp lửa lớn 15 phút đến khi nở tổ ong. | 15
Hoàn thiện | Để nguội, rắc dừa nạo và ăn. | 3
""",
    ),
    dict(
        title="Bánh tét nhân đậu xanh",
        desc="Bánh tét nếp xanh lá chuối, nhân đậu xanh thịt mỡ bùi béo, món không thể thiếu dịp Tết.",
        prep=240,
        cook=480,
        serv=10,
        lvl=4,
        nut=(520, 14, 78, 16, 3, 700),
        ing="""
1 kg | Gạo nếp | ngâm qua đêm
400 g | Đậu xanh cà | ngâm 4 giờ
400 g | Thịt ba chỉ | thái miếng dài
50 g | Hành tím | băm
1 muỗng canh | Muối |
1 muỗng canh | Đường |
1 muỗng canh | Tiêu xay |
1 muỗng canh | Nước mắm |
30 lá | Lá chuối | lau sạch, hơ mềm
50 g | Bột nghệ |
1 muỗng canh | Nước cốt dừa |
1 muỗng canh | Dầu ăn | quét lá chuối cho khỏi dính
""",
        steps="""
Ướp thịt | Ướp thịt với hành, muối, tiêu, nước mắm, đường qua đêm. | 60
Chuẩn bị nếp | Trộn nếp với muối, nước cốt dừa, nghệ; để ráo. | 20
Chuẩn bị đậu | Đồ đậu xanh chín, trộn muối, tiêu, nặn thành khối dài. | 40
Gói bánh | Trải lá chuối, rải nếp, đặt đậu, thịt, phủ nếp rồi cuộn chặt buộc lạt. | 60
Luộc bánh | Xếp bánh vào nồi, đổ ngập nước, luộc 8 tiếng, thường xuyên thêm nước. | 480
Hoàn thiện | Vớt bánh, ép cho ráo nước và để nguội trước khi cắt. | 120
""",
    ),
    dict(
        title="Cà phê sữa đá",
        desc="Cà phê phin đậm đắng hòa cùng sữa đặc béo ngọt, dùng với thật nhiều đá lạnh.",
        prep=5,
        cook=8,
        serv=1,
        lvl=1,
        nut=(130, 3, 22, 4, 0, 60),
        ing="""
20 g | Cà phê xay | rang đậm
2 muỗng canh | Sữa đặc |
100 ml | Nước sôi | 95°C
150 g | Đá viên |
50 ml | Sữa tươi | tùy chọn, cho vị nhẹ hơn
1/2 muỗng cà phê | Bột ca cao | rắc mặt, tùy chọn
1 muỗng cà phê | Đường | tùy chọn
1 nhúm | Muối | tăng vị thơm
1 lát | Vỏ cam | tùy chọn
1 muỗng cà phê | Mật ong | tùy chọn thay đường
1 nhúm | Bột quế | tùy chọn
1 muỗng canh | Nước nóng | làm ẩm cà phê
""",
        steps="""
Cho sữa | Cho sữa đặc vào đáy ly. | 1
Làm ẩm phin | Cho cà phê vào phin, nén nhẹ, thêm chút nước sôi cho nở 30 giây. | 1
Ủ cà phê | Rót nước sôi đầy phin, đậy nắp, chờ cà phê nhỏ giọt khoảng 5 phút. | 6
Khuấy đều | Khuấy cà phê với sữa đặc cho hòa quyện. | 1
Thêm đá | Cho đá viên vào ly, khuấy nhẹ và thưởng thức. | 1
""",
    ),
    dict(
        title="Cà phê trứng Hà Nội",
        desc="Lớp kem trứng đánh bông béo mịn như kem phủ trên cà phê đậm, thức uống đặc sản phố cổ.",
        prep=10,
        cook=5,
        serv=2,
        lvl=2,
        nut=(210, 6, 24, 9, 0, 70),
        ing="""
2 quả | Lòng đỏ trứng gà |
2 muỗng canh | Sữa đặc |
1 muỗng canh | Đường |
100 ml | Cà phê pha đậm | nóng
1 muỗng cà phê | Bơ | tùy chọn
1 nhúm | Muối |
1 muỗng cà phê | Mật ong |
1/2 muỗng cà phê | Vani |
1 chén | Nước nóng | ủ ly
1 muỗng cà phê | Rượu rum | tăng hương, tùy chọn
1 muỗng cà phê | Bột ca cao | rắc mặt
1 muỗng canh | Sữa tươi |
""",
        steps="""
Chuẩn bị cà phê | Pha cà phê đậm, giữ nóng trong ly ủ ấm. | 5
Tách trứng | Tách lấy lòng đỏ, cho vào tô sạch khô. | 2
Đánh kem | Cho sữa đặc, đường, mật ong, vani vào đánh bông 3-4 phút đến khi mịn nhẹ. | 4
Rót cà phê | Rót cà phê vào ly 2/3. | 1
Phủ kem | Múc kem trứng phủ lên, rắc ca cao. | 1
""",
    ),
    dict(
        title="Sinh tố bơ",
        desc="Bơ sáp chín mịn xay cùng sữa đặc và đá, sánh béo mát lạnh, dùng ngay khi vừa xay.",
        prep=10,
        cook=2,
        serv=2,
        lvl=1,
        nut=(330, 5, 32, 21, 7, 60),
        ing="""
2 quả | Bơ sáp | chín
3 muỗng canh | Sữa đặc |
100 ml | Sữa tươi |
150 g | Đá viên |
1 muỗng canh | Đường | tùy chọn
1 muỗng cà phê | Nước cốt chanh |
1 nhúm | Muối |
1 muỗng canh | Sữa chua | tùy chọn
1 muỗng canh | Mật ong | tùy chọn
1 nhánh | Bạc hà | trang trí
1 muỗng canh | Dừa nạo | rắc mặt
1 muỗng cà phê | Vani |
""",
        steps="""
Sơ chế bơ | Bổ đôi bơ, bỏ hạt, dùng thìa múc thịt. | 3
Cho vào máy | Cho bơ, sữa đặc, sữa tươi, chanh, muối vào máy xay. | 2
Xay nhuyễn | Xay 1 phút đến khi mịn, thêm đá xay tiếp 30 giây. | 2
Nếm thử | Nêm lại độ ngọt tùy khẩu vị. | 1
Thưởng thức | Rót ra ly, trang trí dừa nạo và dùng ngay. | 1
""",
    ),
    dict(
        title="Nước mía tắc",
        desc="Nước mía ép tươi mát lạnh thêm chút tắc (quất) chua thanh, giải khát mùa nóng.",
        prep=10,
        cook=3,
        serv=3,
        lvl=1,
        nut=(120, 0, 30, 0, 0, 10),
        ing="""
1 kg | Mía | rửa sạch, cạo vỏ
5 quả | Tắc (quất) | vắt lấy nước
100 g | Đá viên |
1 muỗng canh | Đường | tùy chọn
1 nhúm | Muối |
1 miếng | Gừng | đập dập, tùy chọn
1 lát | Chanh | trang trí
1 nhánh | Bạc hà |
1 quả | Cam | vắt thêm, tùy chọn
1 muỗng canh | Nước cốt chanh | tùy chọn
1 muỗng cà phê | Mật ong |
1 nhánh | Sả | đập dập, tạo mùi thơm
""",
        steps="""
Sơ chế mía | Cắt mía thành khúc, rửa sạch và ép lấy nước. | 6
Vắt tắc | Vắt nước tắc, bỏ hạt. | 3
Trộn nước | Trộn nước mía với nước tắc, gừng, muối nêm nhẹ. | 2
Thêm đá | Cho đá viên vào ly, rót nước mía. | 1
Trang trí | Thêm lát tắc, bạc hà và phục vụ. | 1
""",
    ),
    dict(
        title="Cà phê muối Huế",
        desc="Cà phê đậm phủ lớp kem muối béo mặn nhẹ, hòa quyện vị đắng ngọt đặc trưng xứ Huế.",
        prep=10,
        cook=5,
        serv=1,
        lvl=1,
        nut=(180, 4, 20, 8, 0, 350),
        ing="""
40 ml | Cà phê espresso | hoặc phin đậm
2 muỗng canh | Sữa đặc |
100 ml | Sữa tươi |
50 ml | Kem tươi |
1/4 muỗng cà phê | Muối |
1 muỗng cà phê | Đường |
100 g | Đá viên |
1 muỗng cà phê | Bột ca cao | tùy chọn
1 muỗng canh | Sữa bột béo | tăng độ béo, tùy chọn
1 muỗng cà phê | Mật ong | tùy chọn
1 nhúm | Muối hồng | rắc mặt
1 muỗng cà phê | Vani |
""",
        steps="""
Pha cà phê | Pha 40 ml cà phê espresso hoặc phin đậm, để nguội. | 5
Làm kem muối | Đánh kem tươi với muối, đường, vani cho bông nhẹ. | 3
Cho sữa | Cho sữa đặc, sữa tươi vào ly cùng đá. | 1
Rót cà phê | Rót cà phê lên trên sữa tạo tầng. | 1
Phủ kem | Phủ kem muối lên mặt, rắc chút muối hồng. | 1
""",
    ),
    dict(
        title="Mắm tôm pha chanh đường",
        desc="Mắm tôm đánh bông cùng chanh, đường, ớt và dầu nóng, dùng chấm bún đậu hay chả cá.",
        prep=10,
        cook=3,
        serv=4,
        lvl=1,
        nut=(60, 3, 8, 2, 0, 1500),
        ing="""
3 muỗng canh | Mắm tôm |
2 muỗng canh | Đường |
2 quả | Chanh | vắt lấy nước
1 quả | Ớt | băm
2 tép | Tỏi | băm
1 muỗng canh | Dầu ăn | đun nóng
1 muỗng canh | Rượu trắng |
1 muỗng canh | Nước lọc |
1 nhúm | Tiêu xay |
1 muỗng cà phê | Nước cốt tắc |
1 muỗng canh | Hành phi |
1 nhánh | Rau răm |
""",
        steps="""
Đánh mắm tôm | Cho mắm tôm vào chén, thêm đường, chanh, rượu trắng; dùng đũa đánh cho nổi bọt. | 5
Cho gia vị | Thêm ớt, tỏi, nước tắc, khuấy đều. | 2
Rưới dầu nóng | Rưới dầu nóng lên cho thơm. | 1
Hoàn thiện | Rắc tiêu, hành phi, nếm vừa ăn. | 1
Dùng kèm | Chấm bún đậu, chả cá, thịt luộc. | 1
""",
    ),
    dict(
        title="Dưa cải muối chua",
        desc="Cải bẹ xanh muối chua giòn dai, vị chua nhẹ đặc trưng, ăn kèm thịt kho hoặc nấu canh.",
        prep=20,
        cook=5,
        serv=6,
        lvl=1,
        nut=(25, 1, 5, 0, 2, 900),
        ing="""
1 kg | Cải bẹ xanh | phơi héo
1 lít | Nước lọc |
40 g | Muối hạt |
20 g | Đường |
1 củ | Hành tím | đập dập
1 miếng | Gừng | đập dập
1 củ | Cà rốt | thái lát, tùy chọn
1 quả | Ớt | tùy chọn
1 lá | Lá dứa | tạo mùi thơm
1 muỗng canh | Nước cốt chanh |
1 củ | Tỏi | đập dập
1 nắm | Hẹ | cắt khúc
""",
        steps="""
Phơi cải | Rửa cải, phơi héo nửa ngày cho bớt nước. | 240
Nấu nước muối | Đun sôi nước với muối, đường, để nguội. | 10
Xếp cải | Xếp cải và hẹ vào hũ, thêm gừng, hành. | 8
Đổ nước | Đổ nước muối ngập cải, đè nén chặt. | 3
Ủ chua | Đậy kín, để 2-3 ngày ở nhiệt độ phòng đến khi chua thơm. | 4320
Bảo quản | Cho vào ngăn mát khi đã ưng ý và dùng dần. | 1
""",
    ),
    dict(
        title="Dưa muối xổi",
        desc="Dưa chuột, cải, cà rốt muối xổi giòn chua dịu, ăn ngay trong ngày, hợp bữa cơm gia đình.",
        prep=15,
        cook=5,
        serv=4,
        lvl=1,
        nut=(30, 1, 6, 0, 2, 700),
        ing="""
3 quả | Dưa chuột | thái lát mỏng
1 củ | Cà rốt | thái lát
200 g | Cải thảo | cắt miếng
2 muỗng canh | Muối |
3 muỗng canh | Giấm gạo |
2 muỗng canh | Đường |
300 ml | Nước lọc |
3 tép | Tỏi | thái lát
1 quả | Ớt | thái lát
1 củ | Hành tím | thái lát
1 nắm | Rau răm |
1 muỗng cà phê | Tiêu |
""",
        steps="""
Sơ chế rau | Ướp dưa chuột, cà rốt, cải với chút muối 10 phút, vắt ráo. | 12
Nấu nước ngâm | Đun nước, muối, đường, giấm cho tan, để nguội. | 5
Cho vào hũ | Xếp rau, tỏi, ớt, hành vào hũ. | 3
Đổ nước | Đổ nước ngâm vào cho ngập. | 1
Chờ ngấm | Để 2-3 giờ ngoài tủ hoặc qua đêm trong tủ mát rồi dùng. | 180
""",
    ),
    dict(
        title="Đồ chua cà rốt củ cải",
        desc="Cà rốt và củ cải trắng ngâm giấm đường giòn ngọt chua nhẹ, không thể thiếu trong bánh mì và bún chả.",
        prep=20,
        cook=5,
        serv=6,
        lvl=1,
        nut=(45, 1, 10, 0, 2, 450),
        ing="""
300 g | Củ cải trắng | bào sợi
200 g | Cà rốt | bào sợi
1 muỗng canh | Muối | để ướp rau
100 ml | Giấm gạo |
100 g | Đường |
200 ml | Nước lọc |
1 muỗng cà phê | Muối | pha nước ngâm
2 tép | Tỏi | đập dập
1 quả | Ớt | tùy chọn
1 muỗng canh | Nước cốt chanh |
1 nhúm | Bột nghệ | tạo màu vàng nhẹ, tùy chọn
1 muỗng cà phê | Tiêu |
""",
        steps="""
Ướp rau | Trộn củ cải, cà rốt với muối, để 15 phút rồi vắt ráo. | 15
Nấu nước ngâm | Đun nước, giấm, đường, muối cho tan rồi để nguội. | 5
Xếp vào hũ | Cho rau, tỏi, ớt vào hũ sạch. | 3
Rót nước | Rót nước ngâm đầy cho ngập rau. | 1
Ngâm | Để 3-4 giờ hoặc qua đêm trong tủ lạnh trước khi dùng. | 240
""",
    ),
    dict(
        title="Nem chua Thanh Hóa",
        desc="Nem chua lên men tự nhiên, dai giòn chua cay, gói lá đinh lăng và lá ổi thơm nức.",
        prep=60,
        cook=1,
        serv=8,
        lvl=3,
        nut=(140, 12, 6, 7, 0, 850),
        ing="""
500 g | Thịt nạc đùi heo | xay nhuyễn
100 g | Bì heo | luộc, thái sợi
30 g | Thính gạo |
2 muỗng canh | Muối |
1 muỗng canh | Đường |
3 tép | Tỏi | băm
2 quả | Ớt | thái lát
1 muỗng canh | Tiêu xay |
1 muỗng canh | Nước mắm |
1 muỗng canh | Giấm |
30 lá | Lá đinh lăng |
30 lá | Lá ổi non |
""",
        steps="""
Quết thịt | Trộn thịt với muối, đường, tiêu, quết mịn dẻo. | 15
Trộn bì | Trộn bì heo với thịt, thêm tỏi, ớt, thính, giấm, đảo đều. | 8
Gói nem | Chia thành phần nhỏ, gói lá đinh lăng, lá ổi, buộc lạt. | 30
Ủ nem | Để nem ở nhiệt độ phòng 2-3 ngày cho lên men chua tự nhiên. | 4320
Bảo quản | Chuyển vào tủ mát và dùng trong vài ngày. | 1
Thưởng thức | Ăn cùng tỏi, ớt, lá ổi hoặc rau thơm. | 1
""",
    ),
]
