"""Recipes for categories 1-4. Line formats:
ing:   "<qty> <unit> | <name> | <note>"   (empty qty => no quantity/unit)
steps: "<title> | <description> | <minutes>"  (minutes optional)
nut:   (calories, protein, carbs, fat, fiber, sodium_mg) per serving
"""

RECIPES = [
    dict(
        title="Phở bò Hà Nội",
        desc="Tô phở nước trong, thơm mùi quế hồi và gừng nướng, bánh phở mềm cùng thịt bò tái chín vừa tới.",
        prep=40,
        cook=180,
        serv=6,
        lvl=3,
        nut=(480, 32, 58, 12, 3, 1450),
        ing="""
1.5 kg | Xương ống bò | chần qua nước sôi
500 g | Thịt bắp bò | dùng nạm hoặc gầu tùy thích
300 g | Thịt bò thăn | thái mỏng để chần tái
1 kg | Bánh phở tươi |
1 củ | Gừng | nướng, đập dập
3 củ | Hành tím | nướng cháy vỏ
2 quả | Hoa hồi |
1 thanh | Quế |
3 quả | Thảo quả | rang thơm
2 muỗng canh | Nước mắm ngon |
1 muỗng canh | Muối | nêm nhạt để chấm thêm
1 muỗng canh | Đường phèn |
3 nhánh | Hành lá | thái nhỏ
50 g | Hành tây | thái lát mỏng, ngâm giấm
""",
        steps="""
Chần xương | Cho xương vào nồi nước sôi 5 phút, vớt ra rửa sạch bọt bẩn để nước dùng trong. | 15
Nướng gia vị | Nướng gừng, hành tím cho xém vỏ; rang hoa hồi, quế, thảo quả trên chảo khô đến khi dậy mùi. | 10
Ninh nước dùng | Cho xương, thịt bắp, gừng, hành và gia vị vào nồi nước, hầm lửa nhỏ, thường xuyên vớt bọt. | 150
Nêm nếm | Vớt thịt bắp ra ngâm nước lạnh cho săn, nêm muối, nước mắm, đường phèn cho vừa ăn. | 10
Chuẩn bị tô | Chần bánh phở, xếp thịt bắp thái mỏng và thịt thăn tái lên trên cùng hành lá, hành tây. | 10
Hoàn thiện | Chan nước dùng thật sôi lên tô, ăn kèm chanh, ớt, quẩy và giá đỗ. | 5
""",
    ),
    dict(
        title="Bún bò Huế",
        desc="Nước dùng đậm đà vị sả, mắm ruốc và ớt cay nồng đặc trưng xứ Huế, ăn cùng giò heo và bắp bò.",
        prep=45,
        cook=150,
        serv=6,
        lvl=3,
        nut=(560, 34, 62, 18, 4, 1600),
        ing="""
1 kg | Xương ống heo |
500 g | Bắp bò |
500 g | Giò heo | chặt khúc
1 kg | Bún sợi to |
6 cây | Sả | đập dập, băm nhỏ một phần
2 muỗng canh | Mắm ruốc Huế | hòa với nước, lọc lấy phần trong
2 muỗng canh | Ớt bột | phi cùng dầu
3 muỗng canh | Dầu ăn |
1 quả | Dứa (thơm) | lấy 1/4 quả, thái miếng
3 muỗng canh | Nước mắm |
1 muỗng canh | Đường phèn |
1 muỗng canh | Muối |
200 g | Huyết heo | luộc chín, cắt miếng
100 g | Hành lá, ngò rí | thái nhỏ
300 g | Rau sống | bắp chuối, giá đỗ, rau muống bào
""",
        steps="""
Sơ chế thịt | Chần xương, giò heo và bắp bò qua nước sôi rồi rửa sạch. | 15
Ninh xương | Hầm xương với sả đập dập, dứa và một ít muối khoảng 90 phút, vớt thịt khi chín. | 90
Làm sa tế | Phi thơm sả băm và hành tím, cho ớt bột vào xào lửa nhỏ đến khi dầu đỏ óng. | 10
Hòa mắm ruốc | Để mắm ruốc lắng, chắt phần nước trong đổ vào nồi nước dùng, thêm sa tế, nêm nước mắm và đường. | 15
Chuẩn bị bún | Trụng bún, xếp giò heo, bắp bò thái lát và huyết vào tô. | 10
Thưởng thức | Chan nước dùng sôi, rắc hành ngò, ăn kèm rau sống và chanh. | 5
""",
    ),
    dict(
        title="Bún riêu cua",
        desc="Riêu cua bông xốp trong nước dùng chua thanh từ cà chua, ăn cùng đậu hũ chiên và rau sống.",
        prep=40,
        cook=60,
        serv=4,
        lvl=2,
        nut=(430, 24, 55, 12, 4, 1200),
        ing="""
300 g | Cua đồng xay | lọc lấy nước và gạch
200 g | Thịt heo xay |
2 quả | Trứng gà |
500 g | Bún tươi |
4 quả | Cà chua | bổ múi cau
2 miếng | Đậu hũ chiên | cắt đôi
1 muỗng canh | Mắm tôm | tùy khẩu vị
2 muỗng canh | Me chua | hòa nước lọc
3 nhánh | Hành lá | thái nhỏ
3 củ | Hành tím | băm, phi thơm
1 muỗng canh | Nước mắm |
1 muỗng cà phê | Muối |
1.5 lít | Nước xương heo | hoặc nước lọc
200 g | Rau sống | rau muống chẻ, tía tô, kinh giới
""",
        steps="""
Lọc cua | Hòa cua xay với nước lọc, lọc qua rây để lấy nước cua và gạch. | 10
Trộn riêu | Trộn thịt xay, trứng, hành lá và chút muối, đánh thật đều. | 5
Nấu nước dùng | Đun nước xương, đổ nước cua vào và khuấy nhẹ đến khi riêu nổi thành mảng. | 20
Xào cà chua | Phi hành tím, cho cà chua vào xào mềm rồi đổ vào nồi cùng me chua. | 10
Nêm nếm | Thả đậu hũ chiên, nêm nước mắm, muối cho vừa miệng, nấu thêm 10 phút. | 10
Thưởng thức | Bún trụng nóng xếp vào tô, chan riêu, ăn kèm rau sống và mắm tôm. | 5
""",
    ),
    dict(
        title="Hủ tiếu Nam Vang",
        desc="Sợi hủ tiếu dai mềm trong nước dùng ngọt xương, tôm thịt, trứng cút và tim gan heo thái lát.",
        prep=40,
        cook=120,
        serv=5,
        lvl=3,
        nut=(470, 30, 60, 11, 3, 1350),
        ing="""
1 kg | Xương heo |
300 g | Thịt nạc heo | luộc thái lát
200 g | Tôm sú | bóc vỏ
150 g | Gan heo | luộc chín thái mỏng
500 g | Hủ tiếu khô | ngâm mềm
10 quả | Trứng cút | luộc chín
50 g | Tôm khô | ngâm mềm
1 củ | Củ cải trắng | thái khúc
2 muỗng canh | Nước mắm |
1 muỗng canh | Đường phèn |
1 muỗng cà phê | Muối |
3 củ | Hành tím | phi vàng
100 g | Hẹ | cắt khúc
200 g | Giá đỗ |
""",
        steps="""
Hầm xương | Chần xương, cho vào nồi cùng củ cải, tôm khô hầm 90 phút cho ngọt nước. | 100
Nêm nước dùng | Nêm nước mắm, muối, đường phèn cho hài hòa vị ngọt mặn. | 5
Luộc topping | Luộc chín thịt nạc, gan; trụng tôm sú vừa chín tới rồi để ráo. | 15
Chuẩn bị hủ tiếu | Trụng hủ tiếu qua nước sôi cùng giá và hẹ, cho vào tô. | 5
Bày tô | Xếp thịt, gan, tôm, trứng cút lên trên, rắc hành phi. | 5
Hoàn thiện | Chan nước dùng thật nóng, dùng kèm chanh, ớt, tương đen. | 3
""",
    ),
    dict(
        title="Bún chả cá Nha Trang",
        desc="Chả cá dai giòn chiên vàng trong nước lèo ngọt thanh từ cá và cà chua, vị đặc trưng miền biển.",
        prep=45,
        cook=60,
        serv=4,
        lvl=2,
        nut=(390, 28, 52, 8, 3, 1100),
        ing="""
500 g | Cá thu | xay nhuyễn
300 g | Cá bớp | lấy xương nấu nước dùng
500 g | Bún tươi |
3 quả | Cà chua | bổ múi cau
1 quả | Thơm (dứa) | thái lát mỏng
2 củ | Hành tím | băm
3 nhánh | Hành lá | thái nhỏ
1 muỗng canh | Tiêu xay |
2 muỗng canh | Nước mắm |
1 muỗng cà phê | Muối |
1 muỗng cà phê | Đường |
100 ml | Dầu ăn | chiên chả
200 g | Rau sống | rau muống, giá, bắp chuối
""",
        steps="""
Làm chả cá | Trộn cá xay với tiêu, muối, hành và một ít nước mắm rồi quết dẻo. | 15
Chiên chả | Vo tròn hoặc dàn dẹp thành miếng, chiên vàng hai mặt và để ráo. | 15
Nấu nước lèo | Ninh xương cá với thơm và cà chua 30 phút, nêm nước mắm, đường. | 35
Chuẩn bị bún | Trụng bún, cho vào tô cùng chả cá cắt miếng. | 5
Hoàn thiện | Chan nước lèo, rắc hành lá, ăn kèm rau sống và ớt. | 5
""",
    ),
    dict(
        title="Gỏi cuốn tôm thịt",
        desc="Cuốn bánh tráng thanh mát với tôm, thịt luộc, bún và rau thơm, chấm nước tương đậu phộng.",
        prep=40,
        cook=20,
        serv=4,
        lvl=1,
        nut=(220, 14, 32, 4, 3, 650),
        ing="""
300 g | Tôm sú | luộc, bóc vỏ, chẻ đôi
250 g | Thịt ba chỉ | luộc chín, thái mỏng
20 lá | Bánh tráng | loại vừa
150 g | Bún tươi | trụng chín
1 cây | Xà lách | tách lá
1 bó | Rau thơm | húng, kinh giới
1 bó | Hẹ | cắt bằng chiều dài cuốn
2 muỗng canh | Tương đen |
2 muỗng canh | Đậu phộng rang | giã nhỏ
1 muỗng canh | Đường |
1 muỗng canh | Nước tương |
1 quả | Ớt | thái lát
1 muỗng canh | Tỏi băm |
""",
        steps="""
Luộc nguyên liệu | Luộc thịt ba chỉ và tôm chín tới, để nguội rồi thái, bóc vỏ. | 15
Pha nước chấm | Phi tỏi, cho tương đen, nước tương, đường và một chút nước; nấu sệt, rắc đậu phộng. | 10
Sơ chế rau | Rửa sạch xà lách, rau thơm, để thật ráo. | 5
Nhúng bánh tráng | Nhúng nhanh bánh tráng vào nước ấm rồi trải lên thớt. | 3
Cuốn | Xếp xà lách, bún, rau thơm, thịt; gấp mép, xếp tôm rồi cuộn chặt kèm cọng hẹ. | 15
Thưởng thức | Bày ra đĩa, chấm cùng nước tương đậu phộng. | 2
""",
    ),
    dict(
        title="Bánh cuốn nóng Thanh Trì",
        desc="Lớp bánh tráng mỏng như tờ giấy, nhân thịt mộc nhĩ đậm đà, ăn cùng chả quế và nước chấm chua ngọt.",
        prep=180,
        cook=40,
        serv=4,
        lvl=3,
        nut=(340, 16, 52, 8, 2, 900),
        ing="""
200 g | Bột gạo |
30 g | Bột năng |
500 ml | Nước lọc | chia làm hai phần
1 muỗng canh | Dầu ăn |
200 g | Thịt heo xay |
30 g | Mộc nhĩ | ngâm nở, băm nhỏ
3 củ | Hành khô | băm
1 muỗng cà phê | Tiêu xay |
1 muỗng canh | Nước mắm |
1 muỗng cà phê | Muối |
100 g | Chả quế | thái lát
3 muỗng canh | Nước mắm pha | chua ngọt
1 củ | Cà rốt | thái sợi
""",
        steps="""
Pha bột | Trộn bột gạo, bột năng, muối và nước, khuấy đều, để nghỉ 2 giờ. | 130
Xào nhân | Phi hành, xào thịt xay cùng mộc nhĩ, nêm nước mắm, tiêu cho thơm. | 15
Tráng bánh | Đun nồi nước sôi, căng vải mỏng lên miệng nồi, tráng một lớp bột mỏng. | 5
Hấp chín | Đậy vung khoảng 1 phút cho bột trong, dùng que gỡ bánh ra. | 20
Cuộn bánh | Cho nhân vào giữa, cuộn tròn và phết ít dầu hành lên trên. | 15
Thưởng thức | Ăn kèm chả quế, hành phi, chấm nước mắm chua ngọt và cà rốt ngâm. | 5
""",
    ),
    dict(
        title="Gỏi đu đủ khô bò",
        desc="Đu đủ xanh giòn sần sật trộn khô bò dai ngọt, lạc rang và rau răm, món ăn vặt quen thuộc ở Sài Gòn.",
        prep=20,
        cook=5,
        serv=3,
        lvl=1,
        nut=(260, 12, 30, 9, 4, 850),
        ing="""
400 g | Đu đủ xanh | bào sợi
100 g | Khô bò | xé sợi
1 củ | Cà rốt | bào sợi
3 nhánh | Rau răm |
2 nhánh | Húng quế |
40 g | Đậu phộng rang | giã dập
2 muỗng canh | Nước mắm |
2 muỗng canh | Đường |
2 muỗng canh | Nước cốt chanh |
2 tép | Tỏi | băm
1 quả | Ớt | thái lát
1 muỗng canh | Dầu ăn |
""",
        steps="""
Ngâm đu đủ | Ngâm sợi đu đủ và cà rốt trong nước đá pha chút muối 10 phút để giòn, vắt ráo. | 12
Pha nước trộn | Hòa nước mắm, đường, chanh, tỏi, ớt cho tan đường. | 3
Xé khô bò | Xé khô bò thành sợi vừa ăn, có thể nhúng nhanh trong nước ấm nếu quá cứng. | 3
Trộn gỏi | Trộn đu đủ, cà rốt với nước trộn cho thấm. | 3
Hoàn thiện | Thêm khô bò, rau răm, húng quế, rắc đậu phộng và dùng ngay. | 3
""",
    ),
    dict(
        title="Nem nướng Nha Trang",
        desc="Nem heo nướng thơm cháy cạnh, cuốn bánh tráng với rau sống và chấm nước sốt gan béo ngậy.",
        prep=50,
        cook=25,
        serv=4,
        lvl=2,
        nut=(430, 27, 36, 20, 3, 1000),
        ing="""
500 g | Thịt heo xay | nạc và mỡ tỉ lệ 7:3
2 muỗng canh | Tỏi băm |
2 muỗng canh | Đường |
1 muỗng canh | Nước mắm |
1 muỗng cà phê | Bột ngọt | có thể bỏ
1 muỗng canh | Bột năng |
1 muỗng cà phê | Tiêu xay |
12 cây | Xiên tre | ngâm nước
100 g | Gan heo | luộc, nghiền nhuyễn
2 muỗng canh | Bột gạo | làm nước sốt
20 lá | Bánh tráng |
200 g | Rau sống | xà lách, dưa leo, khế
100 g | Đồ chua |
""",
        steps="""
Ướp thịt | Trộn thịt với tỏi, đường, nước mắm, bột năng, tiêu rồi quết mịn, ướp 30 phút. | 35
Xiên nem | Vo thịt thành cục dài, xiên vào que tre và nén chặt. | 10
Nướng nem | Nướng trên than hoa hoặc lò nướng 200°C khoảng 15 phút, lật đều đến khi vàng. | 20
Nấu nước sốt | Xào gan nghiền với tỏi, cho bột gạo hòa nước, nêm đường, nấu sệt. | 10
Chuẩn bị rau | Rửa rau sống, thái dưa leo, xếp bánh tráng ra đĩa. | 5
Thưởng thức | Cuốn nem với rau, bánh tráng và chấm nước sốt. | 5
""",
    ),
    dict(
        title="Gỏi xa lát cải tím",
        desc="Đĩa gỏi rực rỡ sắc màu với cải tím, cà rốt, dưa leo và chả lụa, món ăn quen thuộc trong mâm cỗ ngày Tết.",
        prep=25,
        cook=5,
        serv=6,
        lvl=1,
        nut=(180, 8, 20, 8, 4, 500),
        ing="""
300 g | Bắp cải tím | thái sợi
2 củ | Cà rốt | bào sợi
2 quả | Dưa leo | thái sợi
150 g | Chả lụa | thái sợi
1 củ | Hành tây | thái lát
100 g | Rau mùi | cắt nhỏ
3 muỗng canh | Dầu ăn |
3 muỗng canh | Giấm gạo |
2 muỗng canh | Đường |
1 muỗng cà phê | Muối |
1 muỗng canh | Đậu phộng rang | giã nhỏ
1 quả | Ớt | thái lát
""",
        steps="""
Ngâm rau | Ngâm cải tím, cà rốt và hành tây trong nước đá 10 phút cho giòn. | 12
Pha nước trộn | Trộn giấm, đường, muối, dầu ăn, ớt cho đều và tan. | 3
Sơ chế chả lụa | Thái chả lụa thành sợi mỏng cùng cỡ với rau. | 5
Trộn gỏi | Vắt ráo rau, cho vào tô lớn cùng dưa leo, chả lụa, rưới nước trộn. | 3
Hoàn thiện | Rắc rau mùi và đậu phộng, bày ra đĩa. | 2
""",
    ),
    dict(
        title="Cơm tấm sườn bì chả",
        desc="Cơm tấm dẻo thơm ăn cùng sườn nướng mật ong, bì thính, chả trứng và nước mắm chua ngọt.",
        prep=60,
        cook=45,
        serv=4,
        lvl=2,
        nut=(720, 38, 78, 26, 3, 1400),
        ing="""
400 g | Gạo tấm |
600 g | Sườn cọng | chặt miếng vừa ăn
2 muỗng canh | Sả băm |
2 muỗng canh | Tỏi băm |
2 muỗng canh | Mật ong |
2 muỗng canh | Nước mắm |
1 muỗng canh | Dầu hào |
150 g | Bì heo | luộc, thái sợi
50 g | Thính gạo | rang, xay
200 g | Thịt heo xay | làm chả trứng
3 quả | Trứng gà |
1 quả | Dưa leo | thái lát
2 quả | Cà chua | thái lát
100 g | Đồ chua |
100 ml | Nước mắm pha | chua ngọt
""",
        steps="""
Ướp sườn | Trộn sườn với sả, tỏi, mật ong, nước mắm, dầu hào, ướp ít nhất 1 giờ. | 60
Nấu cơm tấm | Vo gạo tấm, nấu với lượng nước ít hơn cơm thường một chút cho hạt tơi. | 30
Nướng sườn | Nướng sườn trên than hoặc lò 200°C, quét mật ong, lật đều đến khi vàng cháy cạnh. | 25
Làm chả trứng | Trộn thịt xay, trứng, miến, mộc nhĩ, hấp 25 phút rồi nướng sơ mặt. | 30
Trộn bì | Trộn bì heo với thính gạo, chút muối và tỏi. | 5
Bày đĩa | Xới cơm ra đĩa, xếp sườn, bì, chả, dưa leo, cà chua và chan nước mắm. | 5
""",
    ),
    dict(
        title="Cơm cháy chà bông",
        desc="Cơm cháy giòn rụm chiên vàng, rưới mỡ hành và rắc chà bông thơm, món ăn vặt đặc sản Ninh Bình.",
        prep=30,
        cook=40,
        serv=4,
        lvl=2,
        nut=(450, 10, 60, 19, 1, 620),
        ing="""
400 g | Gạo nếp | ngâm 4 giờ
1 lít | Dầu ăn | để chiên ngập
100 g | Chà bông heo |
3 nhánh | Hành lá | thái nhỏ
2 muỗng canh | Mỡ hành |
1 muỗng cà phê | Muối |
2 muỗng canh | Nước mắm | pha nước chấm
1 muỗng canh | Đường |
1 quả | Ớt | thái lát
1 muỗng canh | Nước cốt chanh |
1 nhánh | Tỏi | băm
100 g | Đậu phộng rang |
""",
        steps="""
Nấu cơm | Nấu nếp với ít nước cho hơi khô, vừa chín tới. | 25
Dàn cơm | Dàn mỏng cơm lên khay có lót giấy nến, nén nhẹ đều tay. | 10
Sấy khô | Phơi nắng hoặc sấy lò 100°C đến khi khô cứng hoàn toàn. | 120
Chiên cơm cháy | Đun dầu thật nóng, chiên từng miếng cơm cháy đến khi nở phồng vàng giòn. | 10
Trang trí | Rưới mỡ hành, rắc chà bông, đậu phộng. | 3
Pha nước chấm | Trộn nước mắm, đường, chanh, tỏi, ớt để chấm kèm. | 5
""",
    ),
    dict(
        title="Cơm lam Tây Nguyên",
        desc="Gạo nếp nấu trong ống nứa thơm mùi lá dong và khói than, ăn cùng muối vừng hoặc thịt nướng.",
        prep=240,
        cook=60,
        serv=6,
        lvl=2,
        nut=(330, 6, 68, 4, 2, 250),
        ing="""
600 g | Gạo nếp nương | ngâm 4 tiếng
1 nắm | Lá chuối | bịt miệng ống
6 lá | Lá dong | lót trong ống
400 ml | Nước cốt dừa |
1 muỗng cà phê | Muối |
50 g | Đậu đen | ngâm nở, tùy chọn
50 g | Đậu xanh cà | tùy chọn
30 g | Vừng (mè) rang |
30 g | Muối ớt | ăn kèm
1 muỗng canh | Đường |
6 cây | Sả | nướng để ăn kèm
""",
        steps="""
Ngâm gạo | Ngâm nếp trong nước lạnh 4 giờ, để ráo. | 240
Trộn nguyên liệu | Trộn nếp với muối, đậu, cốt dừa và đường. | 10
Nhồi ống | Lót lá dong vào ống nứa, nhồi nếp đến 2/3 ống. | 15
Đổ nước | Đổ thêm nước cốt dừa vào cho ngập mặt nếp, bịt đầu ống bằng lá. | 5
Nướng ống | Xếp nghiêng ống trên than hồng, xoay đều khoảng 45 phút đến khi cơm chín, ống cháy xém. | 45
Thưởng thức | Bóc lớp vỏ ống, ăn cơm với muối vừng hoặc thịt nướng. | 5
""",
    ),
    dict(
        title="Cơm niêu Huế",
        desc="Cơm dẻo nấu trong niêu đất có lớp cháy vàng thơm, ăn kèm heo quay và đồ ăn dân dã.",
        prep=30,
        cook=60,
        serv=4,
        lvl=2,
        nut=(650, 28, 70, 28, 3, 1100),
        ing="""
400 g | Gạo thơm |
600 ml | Nước | nấu cơm
400 g | Thịt ba chỉ | quay hoặc rim
1 muỗng canh | Nước mắm |
1 muỗng canh | Đường |
2 muỗng canh | Dầu ăn |
200 g | Đậu hũ | chiên vàng
100 g | Cà tím | nướng, chấm mắm
3 củ | Hành tím | phi thơm
1 muỗng cà phê | Muối |
1 muỗng cà phê | Tiêu |
200 g | Rau sống |
2 quả | Trứng cút | luộc
""",
        steps="""
Vo gạo | Vo gạo sạch, để ráo, cho vào niêu đất cùng nước. | 5
Nấu cơm | Đun niêu trên lửa nhỏ đến khi nước cạn, đậy vung ủ 15 phút. | 30
Tạo lớp cháy | Tăng lửa đều dưới đáy niêu 2 phút để có lớp cháy vàng thơm. | 3
Rim thịt | Rim thịt ba chỉ với nước mắm, đường, hành cho thấm và bóng. | 25
Chiên đậu | Chiên đậu hũ vàng giòn, cắt miếng vừa ăn. | 10
Dọn cơm | Bày niêu cơm ra bàn, ăn kèm thịt rim, đậu hũ, cà tím và rau sống. | 5
""",
    ),
    dict(
        title="Cơm bò xào cần tỏi",
        desc="Bò mềm xào lửa lớn với cần tây và tỏi thơm, dọn nóng trên cơm trắng dẻo.",
        prep=20,
        cook=15,
        serv=3,
        lvl=1,
        nut=(560, 32, 62, 18, 3, 1000),
        ing="""
300 g | Thăn bò | thái mỏng
4 cây | Cần tây | cắt khúc
6 tép | Tỏi | băm
1 củ | Hành tây | thái múi cau
1 muỗng canh | Dầu hào |
1 muỗng canh | Nước tương |
1 muỗng cà phê | Đường |
1/2 muỗng cà phê | Tiêu xay |
1 muỗng cà phê | Bột bắp |
2 muỗng canh | Dầu ăn |
600 g | Cơm nguội |
1 quả | Trứng gà | ốp la, dùng kèm
""",
        steps="""
Ướp bò | Trộn bò với dầu hào, nước tương, tiêu và bột bắp, ướp 15 phút. | 15
Phi tỏi | Đun nóng dầu, phi thơm tỏi băm. | 2
Xào bò | Cho bò vào xào lửa lớn 1-2 phút đến khi vừa chín, xúc ra đĩa. | 3
Xào rau | Xào hành tây và cần tây cùng chút đường 2 phút. | 3
Trộn đều | Cho bò vào lại, đảo nhanh tay, nêm lại vừa ăn. | 2
Dọn cơm | Xúc cơm ra đĩa, xếp bò xào lên trên, thêm trứng ốp la. | 3
""",
    ),
    dict(
        title="Bánh mì thịt nướng",
        desc="Ổ bánh mì giòn rụm kẹp thịt heo nướng sả thơm lừng, đồ chua và rau thơm.",
        prep=40,
        cook=25,
        serv=4,
        lvl=1,
        nut=(520, 24, 60, 20, 3, 1100),
        ing="""
4 ổ | Bánh mì | loại nhỏ
400 g | Thịt heo nạc vai | thái mỏng
2 muỗng canh | Sả băm |
2 muỗng canh | Tỏi băm |
2 muỗng canh | Mật ong |
2 muỗng canh | Nước mắm |
1 muỗng canh | Dầu hào |
1 muỗng cà phê | Tiêu xay |
100 g | Đồ chua |
1 quả | Dưa leo | thái sợi dài
1 bó | Ngò rí |
2 muỗng canh | Bơ | phết bánh
2 muỗng canh | Tương ớt |
""",
        steps="""
Ướp thịt | Ướp thịt với sả, tỏi, mật ong, nước mắm, dầu hào, tiêu ít nhất 30 phút. | 30
Nướng thịt | Nướng thịt trên vỉ than hoặc lò 200°C, mỗi mặt khoảng 5 phút đến khi cháy cạnh. | 12
Làm nóng bánh | Nướng bánh mì lại cho vỏ giòn, rạch một đường dọc. | 3
Phết bơ | Phết bơ, tương ớt lên ruột bánh. | 2
Nhồi nhân | Xếp dưa leo, đồ chua, thịt nướng và ngò rí vào bánh. | 5
Thưởng thức | Dùng nóng ngay khi vỏ còn giòn. | 1
""",
    ),
    dict(
        title="Bánh xèo miền Tây",
        desc="Vỏ bánh vàng giòn nghệ thơm, nhân tôm thịt giá đỗ, cuốn cải xanh chấm nước mắm chua ngọt.",
        prep=45,
        cook=40,
        serv=4,
        lvl=2,
        nut=(480, 22, 50, 22, 4, 1000),
        ing="""
250 g | Bột gạo |
1 muỗng cà phê | Bột nghệ |
400 ml | Nước cốt dừa |
200 ml | Nước lọc |
200 g | Tôm | bóc vỏ
200 g | Thịt ba chỉ | thái mỏng
150 g | Giá đỗ |
1 củ | Hành tây | thái lát
3 nhánh | Hành lá | cắt nhỏ
1 muỗng cà phê | Muối |
100 ml | Dầu ăn |
1 bó | Cải xanh, rau thơm |
100 ml | Nước mắm pha |
""",
        steps="""
Pha bột | Trộn bột gạo, nghệ, muối, nước cốt dừa, nước lọc và hành lá, để nghỉ 30 phút. | 30
Xào nhân | Xào sơ tôm với thịt ba chỉ, nêm nhẹ cho thơm. | 8
Đổ bánh | Đun nóng chảo, thêm dầu, đổ một vá bột xoay tròn cho mỏng. | 3
Cho nhân | Thêm tôm, thịt, hành tây, giá đỗ lên một nửa mặt bánh. | 2
Chiên giòn | Đậy vung 2 phút, mở ra chiên tiếp đến khi vàng giòn, gập đôi. | 6
Thưởng thức | Cuốn bánh với cải xanh, rau thơm, chấm nước mắm chua ngọt. | 5
""",
    ),
    dict(
        title="Bánh khọt Vũng Tàu",
        desc="Bánh nhỏ tròn vàng giòn với tôm tươi và nước cốt dừa, cuốn rau sống chấm nước mắm.",
        prep=40,
        cook=30,
        serv=4,
        lvl=2,
        nut=(420, 16, 46, 20, 3, 900),
        ing="""
200 g | Bột gạo |
50 g | Bột năng |
1 muỗng cà phê | Bột nghệ |
300 ml | Nước cốt dừa |
150 ml | Nước lọc |
200 g | Tôm | bóc vỏ
50 g | Đậu xanh cà | hấp chín
2 muỗng canh | Hành lá | thái nhỏ, phi mỡ hành
100 ml | Dầu ăn |
1 muỗng cà phê | Muối |
1 muỗng cà phê | Đường |
100 g | Rau sống | xà lách, rau thơm
100 ml | Nước mắm pha |
""",
        steps="""
Pha bột | Trộn bột gạo, bột năng, nghệ, nước cốt dừa, nước, muối, đường; nghỉ 30 phút. | 30
Làm nóng khuôn | Đun nóng khuôn bánh khọt, quét dầu vào từng lỗ. | 3
Đổ bột | Rót bột khoảng 2/3 khuôn, đặt tôm lên trên. | 3
Đậy vung | Đậy nắp 3-4 phút đến khi bánh vàng, mép giòn. | 4
Hoàn thiện | Rắc đậu xanh và mỡ hành, gỡ bánh ra đĩa. | 3
Thưởng thức | Cuốn bánh với xà lách, rau thơm, chấm nước mắm chua ngọt. | 5
""",
    ),
    dict(
        title="Bánh bèo Huế",
        desc="Những chiếc bánh bèo nhỏ mịn hấp trong chén, phủ tôm chấy và hành phi, chan nước mắm ngọt cay.",
        prep=60,
        cook=25,
        serv=4,
        lvl=2,
        nut=(330, 12, 55, 6, 2, 780),
        ing="""
250 g | Bột gạo |
30 g | Bột năng |
500 ml | Nước lọc |
1 muỗng cà phê | Muối |
1 muỗng canh | Dầu ăn |
100 g | Tôm khô | băm, rang chấy
50 g | Thịt heo băm | xào
30 g | Hành phi |
50 g | Tóp mỡ |
1 muỗng canh | Mỡ hành |
3 muỗng canh | Nước mắm |
2 muỗng canh | Đường |
1 quả | Ớt | băm
""",
        steps="""
Pha bột | Khuấy bột gạo, bột năng, muối với nước cho tan, để nghỉ 30 phút. | 30
Hấp chén | Quét dầu vào chén nhỏ, đặt vào xửng hấp nóng khoảng 5 phút. | 6
Đổ bột | Rót một vá nhỏ bột vào từng chén, đậy vung hấp 5 phút. | 6
Chuẩn bị topping | Rang tôm chấy, xào thịt băm, phi hành, chuẩn bị tóp mỡ. | 10
Pha nước chấm | Trộn nước mắm, đường, ớt, chút nước ấm. | 3
Hoàn thiện | Rắc tôm chấy, thịt, hành phi, tóp mỡ, rưới mỡ hành và chan nước chấm. | 3
""",
    ),
    dict(
        title="Bánh bột lọc",
        desc="Bánh trong dai với nhân tôm thịt đậm đà, gói lá chuối hấp chín, món ăn xứ Huế mộc mạc.",
        prep=60,
        cook=30,
        serv=4,
        lvl=3,
        nut=(310, 14, 48, 6, 1, 700),
        ing="""
300 g | Bột năng |
300 ml | Nước sôi |
200 g | Tôm | bóc vỏ, băm hoặc để nguyên
150 g | Thịt ba chỉ | thái hạt lựu
3 củ | Hành tím | băm
1 muỗng canh | Nước mắm |
1 muỗng cà phê | Tiêu xay |
1 muỗng cà phê | Đường |
1 muỗng cà phê | Muối |
1 muỗng canh | Dầu ăn |
20 lá | Lá chuối | lau sạch, hơ mềm
100 ml | Nước mắm pha |
1 quả | Ớt |
""",
        steps="""
Nhồi bột | Chế nước sôi từ từ vào bột năng, nhồi đến khi dẻo mịn, đậy ẩm. | 10
Xào nhân | Phi hành, xào tôm và thịt ba chỉ với nước mắm, tiêu, đường. | 10
Chia bột | Chia bột thành viên nhỏ, cán mỏng thành hình tròn. | 15
Cho nhân | Cho nhân vào giữa, gập đôi bánh và ép mép. | 15
Gói lá | Gói mỗi bánh trong lá chuối, xếp vào xửng. | 10
Hấp chín | Hấp lửa lớn 15-20 phút đến khi bánh trong, ăn kèm nước mắm ớt. | 20
""",
    ),
]
