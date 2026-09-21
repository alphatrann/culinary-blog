"""Recipes for categories 5-8 (kho, xào, canh, nướng)."""

RECIPES = [
    dict(
        title="Thịt kho tàu",
        desc="Thịt ba chỉ kho mềm rục trong nước dừa tươi, trứng vịt thấm vị ngọt mặn, món quen thuộc ngày Tết.",
        prep=25,
        cook=90,
        serv=6,
        lvl=2,
        nut=(520, 30, 10, 40, 0, 1100),
        ing="""
800 g | Thịt ba chỉ | cắt khối vuông 4cm
8 quả | Trứng vịt | luộc chín, bóc vỏ
500 ml | Nước dừa tươi |
3 muỗng canh | Nước mắm ngon |
3 muỗng canh | Đường | làm nước màu
4 củ | Hành tím | băm
4 tép | Tỏi | băm
1 muỗng cà phê | Tiêu xay |
1 muỗng cà phê | Muối |
2 quả | Ớt | thái lát
1 muỗng canh | Dầu ăn |
1 muỗng cà phê | Hạt nêm |
""",
        steps="""
Sơ chế thịt | Chần thịt qua nước sôi, rửa sạch, thấm khô. | 10
Ướp thịt | Ướp thịt với hành, tỏi, nước mắm, tiêu, một chút đường khoảng 30 phút. | 30
Làm nước màu | Cho đường và dầu vào nồi, đun đến khi vàng cánh gián thì cho thịt vào đảo. | 10
Kho thịt | Đổ nước dừa ngập thịt, đun sôi rồi hạ lửa nhỏ, kho 60 phút. | 60
Thêm trứng | Cho trứng vào kho thêm 15 phút, nêm nếm cho vừa ăn. | 15
Hoàn thiện | Rắc tiêu và ớt, ăn nóng với cơm trắng và dưa cải. | 3
""",
    ),
    dict(
        title="Cá kho tộ",
        desc="Cá lóc kho trong nồi đất với nước màu caramel, tiêu và ớt, đậm đà đưa cơm.",
        prep=25,
        cook=50,
        serv=4,
        lvl=2,
        nut=(310, 30, 12, 15, 0, 1300),
        ing="""
800 g | Cá lóc | cắt khúc
4 muỗng canh | Nước mắm |
3 muỗng canh | Đường | thắng nước màu
1 muỗng canh | Nước màu |
5 tép | Tỏi | băm
3 củ | Hành tím | băm
2 lát | Gừng | thái sợi
1 muỗng cà phê | Tiêu xay |
2 quả | Ớt | thái lát
200 ml | Nước dừa tươi |
2 nhánh | Hành lá |
1 muỗng canh | Dầu ăn |
""",
        steps="""
Ướp cá | Ướp cá với nước mắm, đường, tiêu, tỏi, hành 30 phút. | 30
Thắng nước màu | Đun đường với dầu đến khi vàng cánh gián rồi tắt bếp. | 8
Xếp cá | Xếp cá vào nồi đất, thêm gừng, đổ nước màu và nước dừa. | 5
Kho cá | Kho lửa nhỏ, không đảo để cá không nát, khoảng 40 phút cho nước sệt. | 40
Nêm nếm | Nêm lại, rắc tiêu, ớt, hành lá. | 3
Thưởng thức | Dọn nóng với cơm trắng và canh chua. | 2
""",
    ),
    dict(
        title="Gà kho sả",
        desc="Đùi gà kho với sả, gừng và nước mắm, da bóng đỏ nâu thơm cay, ăn cơm nóng rất đưa.",
        prep=25,
        cook=40,
        serv=4,
        lvl=1,
        nut=(420, 32, 8, 28, 1, 1050),
        ing="""
800 g | Đùi gà | chặt miếng
5 cây | Sả | băm nhỏ 3 cây, đập dập 2 cây
2 lát | Gừng | thái sợi
4 tép | Tỏi | băm
3 muỗng canh | Nước mắm |
2 muỗng canh | Đường |
1 muỗng canh | Nước màu |
1 muỗng cà phê | Tiêu xay |
2 quả | Ớt | băm
200 ml | Nước dừa tươi | hoặc nước lọc
1 muỗng canh | Dầu ăn |
1 muỗng cà phê | Hạt nêm |
""",
        steps="""
Ướp gà | Trộn gà với sả băm, tỏi, nước mắm, đường, tiêu, ướp 30 phút. | 30
Phi sả | Phi thơm tỏi, sả đập dập với dầu ăn. | 3
Xào gà | Cho gà vào xào săn 5-7 phút đến khi da xém vàng. | 7
Kho gà | Đổ nước dừa, nước màu, đun sôi rồi hạ lửa nhỏ, kho 25 phút. | 25
Hoàn thiện | Thêm ớt, đảo đều, nêm lại và tắt bếp. | 3
""",
    ),
    dict(
        title="Sườn non kho khóm",
        desc="Sườn non kho chua ngọt cùng khóm (dứa), thịt mềm thấm đẫm nước sốt sánh, món cơm miền Nam.",
        prep=25,
        cook=50,
        serv=4,
        lvl=2,
        nut=(440, 26, 30, 24, 2, 1000),
        ing="""
600 g | Sườn non | chặt khúc
1/2 quả | Khóm (dứa) | thái miếng vừa
3 muỗng canh | Nước mắm |
3 muỗng canh | Đường |
4 tép | Tỏi | băm
3 củ | Hành tím | băm
1 muỗng canh | Nước màu |
1 muỗng cà phê | Tiêu xay |
2 quả | Cà chua | bổ múi cau
2 nhánh | Hành lá |
1 muỗng canh | Dầu ăn |
200 ml | Nước lọc |
""",
        steps="""
Chần sườn | Chần sườn qua nước sôi, rửa sạch và để ráo. | 8
Ướp sườn | Ướp sườn với tỏi, hành, nước mắm, đường, tiêu 30 phút. | 30
Xào săn | Phi thơm tỏi hành, xào sườn đến khi săn lại và xém cạnh. | 8
Thêm nước và khóm | Cho nước màu, nước lọc, khóm và cà chua vào, đun sôi. | 5
Kho mềm | Hạ lửa nhỏ, kho 30 phút đến khi sườn mềm, nước sệt. | 30
Hoàn thiện | Rắc hành lá, tiêu và dọn nóng. | 2
""",
    ),
    dict(
        title="Bò kho bánh mì",
        desc="Bò hầm mềm trong nước sốt màu cam thơm quế hồi, ăn kèm bánh mì nóng giòn hoặc bún.",
        prep=30,
        cook=120,
        serv=5,
        lvl=2,
        nut=(520, 34, 45, 22, 4, 1150),
        ing="""
800 g | Bắp bò | cắt khối
3 củ | Cà rốt | cắt khúc
2 cây | Sả | đập dập
2 muỗng canh | Bột bò kho |
1 thanh | Quế |
2 quả | Hoa hồi |
3 quả | Cà chua | băm
1 muỗng canh | Sa tế |
1 muỗng canh | Nước mắm |
1 muỗng canh | Đường |
1 muỗng canh | Muối |
5 tép | Tỏi | băm
5 ổ | Bánh mì | ăn kèm
100 g | Ngò gai, hành lá | thái nhỏ
""",
        steps="""
Ướp bò | Ướp bò với bột bò kho, tỏi, sả băm, muối, đường 1 giờ. | 60
Phi thơm | Phi tỏi, sả, hồi, quế, cho bò vào xào săn. | 10
Hầm bò | Thêm cà chua, sa tế, nước lọc ngập, hầm nhỏ lửa 90 phút. | 90
Thêm cà rốt | Cho cà rốt vào nấu thêm 20 phút cho mềm. | 20
Nêm nếm | Nêm nước mắm, muối, đường; điều chỉnh độ sánh. | 5
Thưởng thức | Múc bò kho ra tô, rắc hành ngò, ăn cùng bánh mì nóng. | 3
""",
    ),
    dict(
        title="Rau muống xào tỏi",
        desc="Rau muống xanh giòn xào lửa lớn với tỏi thơm nức, món rau đơn giản nhưng không thể thiếu.",
        prep=10,
        cook=5,
        serv=3,
        lvl=1,
        nut=(90, 3, 7, 6, 3, 500),
        ing="""
500 g | Rau muống | nhặt, rửa sạch
6 tép | Tỏi | đập dập, băm
2 muỗng canh | Dầu ăn |
1 muỗng cà phê | Nước mắm |
1/2 muỗng cà phê | Muối |
1/2 muỗng cà phê | Đường |
1/2 muỗng cà phê | Hạt nêm |
1/4 muỗng cà phê | Tiêu xay |
1 quả | Ớt | thái lát, tùy chọn
1 muỗng cà phê | Nước cốt chanh | tạo màu xanh
1 muỗng canh | Nước lọc |
""",
        steps="""
Sơ chế | Nhặt rau, cắt khúc 6-7 cm, ngâm nước muối loãng rồi vớt ráo thật kỹ. | 8
Phi tỏi | Đun nóng dầu, phi tỏi băm đến khi dậy mùi (không để cháy). | 2
Xào rau | Cho rau vào, xào lửa lớn, đảo nhanh tay khoảng 2 phút. | 3
Nêm nếm | Nêm muối, nước mắm, đường, hạt nêm và ít nước. | 1
Hoàn thiện | Đảo thêm 30 giây, tắt bếp, rắc tiêu, ớt và dọn ngay. | 1
""",
    ),
    dict(
        title="Bò lúc lắc",
        desc="Bò thăn cắt hạt xúc xắc áp chảo lửa lớn, thơm bơ tỏi, ăn kèm khoai chiên và xà lách.",
        prep=25,
        cook=10,
        serv=3,
        lvl=2,
        nut=(480, 34, 15, 30, 2, 1000),
        ing="""
400 g | Thăn bò | cắt hạt xúc xắc 2cm
1 quả | Ớt chuông đỏ | cắt vuông
1 quả | Ớt chuông xanh | cắt vuông
1 củ | Hành tây | cắt vuông
5 tép | Tỏi | băm
2 muỗng canh | Dầu hào |
1 muỗng canh | Nước tương |
1 muỗng canh | Bơ |
1 muỗng cà phê | Đường |
1 muỗng cà phê | Tiêu đen |
2 muỗng canh | Dầu ăn |
1 cây | Xà lách | lót đĩa
2 quả | Cà chua | thái lát
""",
        steps="""
Ướp bò | Ướp bò với dầu hào, nước tương, đường, tiêu, tỏi 20 phút. | 20
Áp chảo bò | Nóng chảo thật nóng, cho bò vào lắc đều 1-2 phút đến khi xém cạnh, xúc ra. | 4
Xào rau | Xào ớt chuông và hành tây nhanh tay cho giòn. | 3
Cho bơ | Cho bơ tan chảy, thêm bò trở lại, đảo đều 30 giây. | 2
Bày đĩa | Lót xà lách, cà chua, xếp bò lúc lắc lên trên. | 3
""",
    ),
    dict(
        title="Ốc xào rau muống",
        desc="Ốc bươu xào giòn với rau muống và tỏi, món nhậu dân dã đậm đà vị Bắc.",
        prep=45,
        cook=15,
        serv=3,
        lvl=2,
        nut=(200, 18, 12, 9, 2, 850),
        ing="""
500 g | Ốc bươu | rửa sạch, luộc chín
300 g | Rau muống | nhặt, cắt khúc
5 tép | Tỏi | băm
2 củ | Hành tím | băm
2 muỗng canh | Dầu ăn |
1 muỗng canh | Nước mắm |
1 muỗng cà phê | Đường |
1/2 muỗng cà phê | Muối |
1 muỗng cà phê | Tiêu xay |
1 quả | Ớt | thái lát
3 lá | Lá lốt | thái sợi
1 muỗng canh | Nước cốt chanh |
""",
        steps="""
Luộc ốc | Luộc ốc với chút gừng, sả 10 phút, tách thịt bỏ phần ruột đen. | 15
Ướp ốc | Trộn ốc với nước mắm, đường, tiêu 10 phút. | 10
Phi tỏi | Phi thơm tỏi và hành tím với dầu. | 2
Xào ốc | Cho ốc vào xào lửa lớn 3 phút, thêm rau muống. | 5
Hoàn thiện | Xào thêm 2 phút, rắc lá lốt, ớt, chanh, dọn ngay. | 3
""",
    ),
    dict(
        title="Bò xào hành tây",
        desc="Bò mềm ngọt xào cùng hành tây giòn thơm, nêm đậm đà, nhanh gọn cho bữa cơm gia đình.",
        prep=20,
        cook=8,
        serv=3,
        lvl=1,
        nut=(380, 30, 12, 22, 2, 900),
        ing="""
350 g | Thăn bò | thái lát mỏng
2 củ | Hành tây | thái múi cau
4 tép | Tỏi | băm
1 muỗng canh | Nước tương |
1 muỗng canh | Dầu hào |
1 muỗng cà phê | Đường |
1 muỗng cà phê | Bột bắp |
1/2 muỗng cà phê | Tiêu |
2 muỗng canh | Dầu ăn |
1 nhánh | Hành lá | cắt khúc
1 quả | Cà chua | bổ múi
1 muỗng cà phê | Dầu mè |
""",
        steps="""
Ướp bò | Trộn bò với nước tương, dầu hào, bột bắp, tiêu và tỏi 15 phút. | 15
Xào bò | Nóng chảo, xào bò lửa lớn 1 phút cho săn, xúc ra. | 2
Xào hành | Xào hành tây với chút đường đến khi vừa mềm nhưng còn giòn. | 3
Trộn đều | Cho bò vào lại, thêm hành lá, cà chua và dầu mè. | 2
Thưởng thức | Dọn nóng với cơm trắng. | 1
""",
    ),
    dict(
        title="Phở xào bò",
        desc="Sợi phở xào giòn nhẹ với bò mềm và rau cải, thấm vị nước tương và tỏi, món sáng hấp dẫn.",
        prep=20,
        cook=10,
        serv=3,
        lvl=1,
        nut=(510, 24, 65, 16, 3, 1100),
        ing="""
500 g | Bánh phở tươi | tách rời sợi
250 g | Thăn bò | thái mỏng
200 g | Cải ngọt | cắt khúc
1 củ | Cà rốt | thái sợi
1 củ | Hành tây | thái múi cau
4 tép | Tỏi | băm
2 muỗng canh | Nước tương |
1 muỗng canh | Dầu hào |
1 muỗng cà phê | Đường |
1/2 muỗng cà phê | Tiêu xay |
3 muỗng canh | Dầu ăn |
2 nhánh | Hành lá | cắt khúc
""",
        steps="""
Ướp bò | Ướp bò với nước tương, dầu hào, tiêu, tỏi 15 phút. | 15
Xào bò | Xào bò lửa lớn 1 phút rồi xúc ra đĩa. | 2
Xào rau | Xào cà rốt, hành tây, cải ngọt trong dầu nóng 2 phút. | 3
Xào phở | Cho phở vào chảo lớn, đảo nhẹ tay cùng nước tương và đường. | 4
Hoàn thiện | Thêm bò trở lại, hành lá, đảo đều và dọn ngay. | 2
""",
    ),
    dict(
        title="Canh chua cá lóc",
        desc="Nước canh chua thanh ngọt từ me, dứa và cà chua, cá lóc mềm cùng bạc hà, giá và rau om.",
        prep=25,
        cook=25,
        serv=4,
        lvl=2,
        nut=(210, 24, 14, 6, 3, 900),
        ing="""
500 g | Cá lóc | cắt khúc
2 quả | Cà chua | bổ múi
1/4 quả | Dứa (thơm) | thái lát
100 g | Đậu bắp | cắt xéo
100 g | Bạc hà (dọc mùng) | thái xéo
100 g | Giá đỗ |
2 muỗng canh | Me chua | ngâm, lọc lấy nước
2 muỗng canh | Nước mắm |
1 muỗng canh | Đường |
1/2 muỗng cà phê | Muối |
3 tép | Tỏi | phi thơm
1 nhánh | Ngò om, ngò gai | thái nhỏ
""",
        steps="""
Sơ chế cá | Ướp cá với chút muối, tiêu; khử tanh bằng gừng. | 10
Nấu nước dùng | Đun nước me với dứa và cà chua, nêm nước mắm, đường. | 8
Cho cá | Khi nước sôi, thả cá vào nấu 5-7 phút đến khi chín. | 7
Thêm rau | Cho bạc hà, đậu bắp, giá đỗ, nấu sôi lại rồi tắt bếp. | 3
Hoàn thiện | Rắc tỏi phi, ngò om, ngò gai, dọn nóng. | 2
""",
    ),
    dict(
        title="Canh khổ qua nhồi thịt",
        desc="Khổ qua (mướp đắng) nhồi thịt heo mộc nhĩ, nấu nước trong ngọt, món canh giải nhiệt ngày Tết.",
        prep=30,
        cook=40,
        serv=4,
        lvl=2,
        nut=(190, 14, 10, 10, 3, 750),
        ing="""
3 quả | Khổ qua | cắt khúc, bỏ ruột
250 g | Thịt heo xay |
20 g | Mộc nhĩ | ngâm, băm
20 g | Miến | ngâm, cắt ngắn
2 củ | Hành tím | băm
1 muỗng cà phê | Tiêu xay |
1 muỗng canh | Nước mắm |
1 muỗng cà phê | Muối |
1 muỗng cà phê | Hạt nêm |
1 lít | Nước xương | hoặc nước lọc
2 nhánh | Hành lá, ngò rí | thái nhỏ
1 muỗng canh | Dầu ăn |
""",
        steps="""
Sơ chế khổ qua | Cắt khúc, bỏ ruột, chần nhanh nước sôi pha muối cho bớt đắng. | 8
Trộn nhân | Trộn thịt xay, mộc nhĩ, miến, hành, tiêu, nước mắm. | 5
Nhồi nhân | Nhồi nhân đều vào từng khúc khổ qua. | 10
Nấu canh | Đun sôi nước xương, thả khổ qua vào nấu lửa vừa 25 phút. | 25
Nêm nếm | Nêm muối, hạt nêm, rắc hành ngò. | 2
""",
    ),
    dict(
        title="Súp cua trứng bắc thảo",
        desc="Súp sánh mịn với thịt cua, trứng bắc thảo và trứng gà đánh tan, ấm bụng ngày se lạnh.",
        prep=25,
        cook=25,
        serv=4,
        lvl=2,
        nut=(210, 16, 18, 9, 1, 900),
        ing="""
150 g | Thịt cua | tách sẵn
2 quả | Trứng bắc thảo | cắt hạt lựu
2 quả | Trứng gà | đánh tan
100 g | Nấm rơm | cắt nhỏ
1 lít | Nước xương gà |
3 muỗng canh | Bột năng | hòa nước
2 củ | Hành tím | phi thơm
1 muỗng canh | Nước mắm |
1/2 muỗng cà phê | Muối |
1/2 muỗng cà phê | Tiêu trắng |
1 nhánh | Hành lá, ngò rí |
1 muỗng cà phê | Dầu mè |
""",
        steps="""
Phi hành | Phi thơm hành tím, xào nấm rơm và thịt cua trong 2 phút. | 5
Nấu nước súp | Đổ nước xương gà, đun sôi, nêm nước mắm, muối. | 8
Làm sánh | Hòa bột năng với nước, đổ từ từ vào nồi, khuấy đều cho sánh. | 5
Thêm trứng | Rót trứng gà đánh tan thành sợi mảnh, khuấy nhẹ. | 3
Hoàn thiện | Cho trứng bắc thảo, tiêu, dầu mè, hành ngò và dọn nóng. | 2
""",
    ),
    dict(
        title="Canh bí đao nấu tôm",
        desc="Canh thanh nhẹ ngọt nước, bí đao mềm nấu cùng tôm tươi, giải nhiệt mùa hè.",
        prep=15,
        cook=15,
        serv=4,
        lvl=1,
        nut=(90, 11, 6, 2, 1, 700),
        ing="""
400 g | Bí đao | gọt vỏ, cắt miếng
200 g | Tôm tươi | bóc vỏ
2 củ | Hành tím | băm
1 muỗng canh | Nước mắm |
1/2 muỗng cà phê | Muối |
1/2 muỗng cà phê | Hạt nêm |
1/4 muỗng cà phê | Tiêu xay |
800 ml | Nước lọc |
1 nhánh | Hành lá |
1 nhánh | Ngò rí |
1 muỗng cà phê | Dầu ăn |
""",
        steps="""
Ướp tôm | Ướp tôm với hành, tiêu, chút muối 10 phút. | 10
Xào tôm | Phi hành với dầu, xào tôm đến khi chuyển màu. | 3
Nấu bí | Đổ nước vào, đun sôi rồi cho bí đao vào nấu 8 phút. | 8
Nêm nếm | Nêm nước mắm, muối, hạt nêm vừa ăn. | 2
Hoàn thiện | Rắc hành lá, ngò rí rồi tắt bếp. | 1
""",
    ),
    dict(
        title="Canh bắp cải cuộn thịt",
        desc="Cuộn lá cải xanh non mềm bọc thịt heo xay trong nước canh ngọt trong, đơn giản mà cuốn hút.",
        prep=30,
        cook=25,
        serv=4,
        lvl=2,
        nut=(170, 15, 8, 9, 3, 700),
        ing="""
1 cây | Bắp cải | tách lá, chần mềm
250 g | Thịt heo xay |
20 g | Mộc nhĩ | ngâm, băm
20 g | Miến | ngâm, cắt ngắn
1 củ | Hành tím | băm
1 muỗng canh | Nước mắm |
1 muỗng cà phê | Tiêu xay |
1/2 muỗng cà phê | Muối |
1 lít | Nước xương |
1 nhánh | Hành lá | buộc cuộn
1 củ | Cà rốt | thái lát hoa
1 muỗng cà phê | Hạt nêm |
""",
        steps="""
Chần lá cải | Chần lá bắp cải qua nước sôi cho mềm, cắt bỏ gân cứng. | 5
Trộn nhân | Trộn thịt xay, mộc nhĩ, miến, hành, tiêu, nước mắm. | 5
Cuộn | Cho nhân lên lá cải, cuộn chặt như cuốn nem, buộc bằng hành lá. | 12
Nấu nước dùng | Đun sôi nước xương, nêm muối, hạt nêm. | 5
Nấu chín | Thả cuộn cải và cà rốt vào nấu 15 phút đến khi chín, dọn nóng. | 15
""",
    ),
    dict(
        title="Thịt heo nướng sả",
        desc="Thịt heo tẩm sả thơm nướng than cháy cạnh, ăn cùng bún, rau sống và nước mắm chua ngọt.",
        prep=40,
        cook=20,
        serv=4,
        lvl=1,
        nut=(420, 28, 15, 27, 1, 900),
        ing="""
600 g | Thịt heo nạc vai | thái mỏng
4 cây | Sả | băm nhỏ
4 tép | Tỏi | băm
2 muỗng canh | Đường |
2 muỗng canh | Nước mắm |
1 muỗng canh | Dầu hào |
1 muỗng canh | Mật ong |
1 muỗng cà phê | Tiêu xay |
1 muỗng canh | Dầu ăn |
1 muỗng canh | Vừng (mè) rang |
300 g | Bún tươi | ăn kèm
100 ml | Nước mắm pha |
""",
        steps="""
Ướp thịt | Trộn thịt với sả, tỏi, đường, nước mắm, dầu hào, mật ong, tiêu, ướp 30 phút. | 30
Xiên thịt | Xiên thịt vào que hoặc để nguyên miếng. | 5
Nướng | Nướng trên than hoặc lò 200°C mỗi mặt 4-5 phút đến khi cháy cạnh. | 12
Quét mật ong | Quét thêm mật ong pha dầu để thịt bóng. | 2
Thưởng thức | Ăn nóng với bún, rau sống, nước mắm chua ngọt. | 3
""",
    ),
    dict(
        title="Chả cá Lã Vọng",
        desc="Cá lăng ướp nghệ nướng thơm rồi rán trên chảo cùng thì là, hành lá, ăn với bún và mắm tôm.",
        prep=180,
        cook=25,
        serv=4,
        lvl=3,
        nut=(480, 32, 30, 25, 2, 900),
        ing="""
600 g | Phi lê cá lăng | thái miếng
2 muỗng canh | Bột nghệ |
2 củ | Riềng | giã lấy nước
2 muỗng canh | Mẻ | lọc lấy nước
2 muỗng canh | Mắm tôm |
2 muỗng canh | Dầu ăn |
200 g | Thì là | cắt khúc
100 g | Hành lá | cắt khúc
300 g | Bún tươi |
50 g | Đậu phộng rang |
1 quả | Chanh | vắt lấy nước
100 g | Rau thơm | húng, tía tô
""",
        steps="""
Ướp cá | Trộn cá với nghệ, riềng, mẻ, mắm tôm, ướp ít nhất 3 giờ. | 180
Nướng cá | Nướng cá trên than hoa hoặc lò 200°C, mỗi mặt 5 phút. | 10
Chuẩn bị chảo | Đặt chảo lên bàn, đun nóng dầu. | 3
Rán cá | Cho cá vào chảo rán sơ cùng thì là, hành lá 3 phút. | 5
Pha mắm tôm | Đánh mắm tôm với chanh, đường, chút ớt cho nổi bọt. | 3
Thưởng thức | Ăn nóng với bún, đậu phộng, rau thơm, chấm mắm tôm. | 5
""",
    ),
    dict(
        title="Bò nướng lá lốt",
        desc="Bò xay ướp đậm bọc lá lốt xanh thơm nướng than, chấm mắm nêm hoặc nước mắm chua ngọt.",
        prep=40,
        cook=15,
        serv=4,
        lvl=2,
        nut=(310, 24, 8, 21, 1, 800),
        ing="""
400 g | Thịt bò xay | thêm 50g mỡ heo xay
30 lá | Lá lốt | rửa sạch
3 cây | Sả | băm nhỏ
4 tép | Tỏi | băm
2 củ | Hành tím | băm
1 muỗng canh | Đường |
1 muỗng canh | Nước mắm |
1 muỗng canh | Dầu hào |
1 muỗng cà phê | Tiêu xay |
1 muỗng cà phê | Bột nghệ |
1 muỗng canh | Dầu ăn |
100 ml | Nước mắm pha | chấm
""",
        steps="""
Ướp thịt | Trộn thịt bò với sả, tỏi, hành, đường, nước mắm, dầu hào, tiêu, ướp 30 phút. | 30
Cuốn lá | Đặt thịt lên mặt lá lốt, cuộn chặt thành cuốn nhỏ. | 15
Xiên que | Xiên 3-4 cuốn một que hoặc để nguyên. | 5
Nướng | Nướng than nhỏ lửa, xoay đều 10-12 phút đến khi lá xém và thịt chín. | 12
Thưởng thức | Ăn nóng với bún, rau sống, chấm nước mắm chua ngọt. | 3
""",
    ),
    dict(
        title="Gà nướng mật ong",
        desc="Gà nguyên con hoặc đùi gà ướp mật ong, tỏi, nướng vàng bóng, da giòn thịt mềm thơm ngọt.",
        prep=30,
        cook=60,
        serv=4,
        lvl=2,
        nut=(480, 38, 18, 27, 0, 900),
        ing="""
1 kg | Đùi gà góc tư |
4 muỗng canh | Mật ong |
3 muỗng canh | Nước tương |
1 muỗng canh | Dầu hào |
5 tép | Tỏi | băm nhuyễn
1 muỗng canh | Gừng | băm
1 muỗng cà phê | Tiêu xay |
1 muỗng cà phê | Muối |
1 muỗng canh | Dầu ăn |
1 muỗng cà phê | Ngũ vị hương |
2 củ | Khoai tây | cắt múi
1 nhánh | Hương thảo |
""",
        steps="""
Ướp gà | Trộn tất cả gia vị với mật ong, xoa đều lên gà và ướp 2 giờ trong tủ mát. | 30
Làm nóng lò | Làm nóng lò ở 200°C. | 10
Nướng lần 1 | Xếp gà lên khay cùng khoai tây, nướng 30 phút. | 30
Phết mật ong | Lật gà, phết thêm hỗn hợp ướp, nướng tiếp 20 phút đến khi vàng bóng. | 20
Nghỉ thịt | Để gà nghỉ 10 phút rồi cắt miếng dọn ăn. | 10
""",
    ),
    dict(
        title="Cá lóc nướng trui",
        desc="Cá lóc nguyên con nướng vùi trong rơm, da cháy thịt trắng ngọt, cuốn bánh tráng rau sống chấm mắm me.",
        prep=30,
        cook=40,
        serv=4,
        lvl=2,
        nut=(260, 34, 12, 8, 2, 700),
        ing="""
1 con | Cá lóc | khoảng 1 kg, làm sạch
1 nắm | Rơm khô | để nướng
20 lá | Bánh tráng |
200 g | Rau sống | xà lách, chuối chát, khế
100 g | Bún tươi |
3 muỗng canh | Mắm me | hoặc nước mắm me
2 quả | Ớt | băm
3 tép | Tỏi | băm
1 muỗng canh | Đường |
1 muỗng canh | Nước cốt chanh |
1 muỗng canh | Hành phi |
1 muỗng cà phê | Muối |
""",
        steps="""
Sơ chế cá | Cạo sạch nhớt, xiên xuyên thân cá bằng que tre, để nguyên da. | 10
Đốt rơm | Đốt rơm ngoài trời, để lửa cháy rồi rút, tạo than hồng. | 10
Nướng trui | Vùi cá vào rơm còn nóng, nướng 25-30 phút đến khi da cháy đen thịt chín. | 30
Lột da | Đập cháy da bên ngoài, lột sạch, giữ thịt trắng. | 5
Pha nước chấm | Trộn mắm me, đường, chanh, tỏi ớt. | 5
Thưởng thức | Cuốn cá với bánh tráng, rau sống, bún, chấm mắm me. | 5
""",
    ),
]
