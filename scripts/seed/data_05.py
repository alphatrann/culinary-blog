"""Recipes for categories 17-20 (xôi/cháo, mì/miến, món Âu, món Á)."""

RECIPES = [
    dict(
        title="Xôi gấc",
        desc="Xôi nếp đỏ óng màu gấc, thơm mùi vani và dẻo mềm, món không thể thiếu trong các dịp lễ.",
        prep=240,
        cook=40,
        serv=6,
        lvl=2,
        nut=(390, 7, 78, 6, 2, 120),
        ing="""
500 g | Gạo nếp | ngâm 4 giờ
1 quả | Gấc chín | lấy thịt và hạt
50 ml | Rượu trắng | trộn gấc
3 muỗng canh | Đường |
1/2 muỗng cà phê | Muối |
2 muỗng canh | Dầu ăn |
1 muỗng cà phê | Vani |
100 ml | Nước cốt dừa |
1 muỗng canh | Dừa nạo |
1 muỗng canh | Mỡ heo |
1 muỗng canh | Vừng (mè) rang |
1/2 muỗng cà phê | Bột nghệ |
""",
        steps="""
Ngâm nếp | Ngâm nếp 4 giờ, đãi sạch, để ráo. | 240
Trộn gấc | Trộn thịt gấc với rượu, dầu ăn và vani thật đều. | 5
Ủ nếp | Trộn gấc vào nếp, thêm muối, đường, ủ 30 phút. | 30
Đồ xôi | Xếp nếp vào xửng, đồ lửa lớn 30-35 phút, đảo giữa chừng. | 35
Thêm béo | Rưới nước cốt dừa và mỡ, xới đều. | 3
Hoàn thiện | Đồ thêm 5 phút, rắc vừng dừa nạo và dọn ăn. | 5
""",
    ),
    dict(
        title="Xôi xéo",
        desc="Xôi nếp vàng bùi với đậu xanh nghiền, hành phi giòn thơm, món ăn sáng quen thuộc của Hà Nội.",
        prep=240,
        cook=45,
        serv=4,
        lvl=2,
        nut=(430, 11, 70, 12, 3, 350),
        ing="""
400 g | Gạo nếp | ngâm 4 giờ
150 g | Đậu xanh cà | ngâm 2 giờ
1 muỗng cà phê | Bột nghệ |
1/2 muỗng cà phê | Muối |
5 củ | Hành khô | thái lát, phi vàng
3 muỗng canh | Dầu ăn | phi hành
1 muỗng cà phê | Đường |
1 nhánh | Hành lá |
1 cái | Lá chuối | lót
50 g | Mỡ heo | cho béo
1 muỗng canh | Vừng (mè) rang |
1 nhúm | Tiêu xay |
""",
        steps="""
Ngâm nguyên liệu | Ngâm nếp và đậu xanh riêng 4 giờ và 2 giờ. | 240
Đồ xôi | Trộn nếp với nghệ, muối, đồ chín trong 30 phút. | 30
Đồ đậu xanh | Đồ đậu xanh đến khi chín mềm, nghiền nhuyễn. | 20
Phi hành | Phi hành khô vàng giòn với dầu, tách riêng hành và dầu. | 10
Nặn xôi | Nặn xôi thành khối, phủ đậu xanh nghiền. | 5
Hoàn thiện | Rắc hành phi, rưới dầu hành lên trên và dọn ngay. | 2
""",
    ),
    dict(
        title="Cháo lòng",
        desc="Cháo gạo nhừ nấu nước luộc lòng heo, ăn cùng dồi, tim, gan, tiêu và hành, đậm đà ấm bụng.",
        prep=45,
        cook=90,
        serv=5,
        lvl=3,
        nut=(380, 22, 38, 15, 2, 1100),
        ing="""
200 g | Gạo tẻ |
1.5 lít | Nước luộc lòng |
300 g | Lòng heo | làm sạch
100 g | Tim heo |
100 g | Gan heo |
100 g | Dồi heo |
5 củ | Hành khô |
2 muỗng canh | Nước mắm |
1 muỗng cà phê | Muối |
1 muỗng cà phê | Tiêu xay |
3 nhánh | Hành lá, ngò rí |
2 quả | Ớt |
""",
        steps="""
Sơ chế lòng | Rửa lòng với muối, giấm, chanh cho sạch mùi, chần sơ. | 20
Luộc lòng | Luộc lòng, tim, gan, dồi chín, thái miếng, giữ nước luộc. | 30
Nấu cháo | Xào gạo với hành khô, đổ nước luộc lòng, nấu nhừ 45 phút. | 45
Nêm nếm | Nêm nước mắm, muối cho vừa ăn. | 3
Múc cháo | Cho lòng, dồi vào tô, chan cháo nóng. | 3
Hoàn thiện | Rắc hành ngò, tiêu, ăn kèm ớt và quẩy. | 2
""",
    ),
    dict(
        title="Cháo gà hành gừng",
        desc="Cháo gà mềm sánh thơm gừng, thịt gà xé phay, thích hợp cho ngày ốm hay se lạnh.",
        prep=25,
        cook=60,
        serv=4,
        lvl=1,
        nut=(310, 24, 38, 6, 1, 800),
        ing="""
200 g | Gạo tẻ |
600 g | Gà ta | nửa con
2 lít | Nước lọc |
3 lát | Gừng | thái sợi
3 củ | Hành tím |
1 muỗng canh | Nước mắm |
1 muỗng cà phê | Muối |
1/2 muỗng cà phê | Tiêu |
3 nhánh | Hành lá |
1 nhánh | Rau răm |
1 muỗng canh | Hành phi |
1/2 muỗng cà phê | Hạt nêm |
""",
        steps="""
Luộc gà | Luộc gà với gừng, hành tím 25 phút, vớt ra để nguội, xé phay. | 25
Nấu cháo | Rang gạo sơ, đổ nước luộc gà nấu nhừ 35 phút. | 35
Nêm cháo | Nêm nước mắm, muối, hạt nêm. | 3
Chuẩn bị tô | Cho thịt gà, gừng sợi vào tô. | 3
Hoàn thiện | Múc cháo nóng, rắc hành lá, rau răm, tiêu, hành phi. | 2
""",
    ),
    dict(
        title="Xôi ngũ sắc",
        desc="Xôi nhiều màu từ lá cẩm, nghệ, gấc, lá dứa, rực rỡ trên mâm cỗ dân tộc Tày, Nùng.",
        prep=240,
        cook=45,
        serv=6,
        lvl=3,
        nut=(380, 7, 78, 5, 2, 100),
        ing="""
500 g | Gạo nếp | ngâm 4 giờ
100 g | Lá cẩm | nấu lấy nước tím
1 muỗng cà phê | Bột nghệ | màu vàng
1 quả | Gấc | màu đỏ
5 lá | Lá dứa | màu xanh
1 muỗng cà phê | Muối |
2 muỗng canh | Dầu ăn |
1 muỗng canh | Đường |
50 ml | Nước cốt dừa |
1 muỗng canh | Vừng (mè) rang |
1 muỗng canh | Mỡ heo |
1 muỗng cà phê | Vani |
""",
        steps="""
Chuẩn bị màu | Nấu lá cẩm, nghệ, gấc, lá dứa lấy nước, để nguội. | 20
Nhuộm nếp | Chia nếp làm 5 phần, ngâm mỗi phần một màu 3-4 giờ. | 240
Trộn nếp | Vớt ráo, trộn với muối, dầu, đường. | 5
Đồ xôi | Đồ từng màu riêng trong xửng 30 phút. | 30
Ghép màu | Trộn nhẹ các màu, xếp vào khuôn hoặc lá chuối. | 10
Hoàn thiện | Rưới nước cốt dừa, rắc vừng và dọn ăn. | 3
""",
    ),
    dict(
        title="Mì Quảng",
        desc="Sợi mì bản to vàng ươm, nước lèo sánh ít mà đậm, ăn kèm bánh tráng nướng, đậu phộng và rau sống.",
        prep=40,
        cook=45,
        serv=4,
        lvl=3,
        nut=(560, 30, 70, 17, 4, 1200),
        ing="""
500 g | Mì Quảng tươi |
300 g | Thịt heo ba chỉ |
200 g | Tôm sú | bóc vỏ
1 muỗng canh | Bột nghệ |
4 củ | Hành tím | băm
4 tép | Tỏi | băm
500 ml | Nước xương heo |
2 muỗng canh | Nước mắm |
1 muỗng cà phê | Đường |
50 g | Đậu phộng rang | giã dập
2 tờ | Bánh tráng nướng |
200 g | Rau sống | giá, rau muống, bắp chuối
""",
        steps="""
Ướp thịt tôm | Ướp thịt và tôm với nghệ, hành tỏi, đường, nước mắm 20 phút. | 20
Xào nhân | Phi thơm hành tỏi, xào thịt tôm đến săn. | 10
Nấu nước lèo | Đổ nước xương, nấu lửa nhỏ 20 phút cho cạn còn sánh. | 25
Chuẩn bị mì | Chần mì Quảng với nước sôi, để ráo. | 3
Bày tô | Xếp rau sống, mì, thịt tôm vào tô, chan lèo. | 3
Hoàn thiện | Rắc đậu phộng, bẻ bánh tráng, thêm ớt và chanh. | 2
""",
    ),
    dict(
        title="Miến gà",
        desc="Miến dai mềm trong nước dùng gà ngọt thanh, thịt gà xé phay và rau thơm ăn nóng.",
        prep=30,
        cook=60,
        serv=4,
        lvl=2,
        nut=(390, 28, 50, 8, 2, 950),
        ing="""
200 g | Miến dong |
1 con | Gà ta | khoảng 1 kg
2 củ | Hành tây | nướng
1 củ | Gừng | nướng
3 củ | Hành tím | nướng
20 g | Nấm hương | ngâm nở
20 g | Nấm mèo | ngâm, thái sợi
1 muỗng canh | Nước mắm |
1 muỗng cà phê | Muối |
1/2 muỗng cà phê | Tiêu |
2 nhánh | Hành lá, ngò rí | thái nhỏ
1 nhánh | Rau răm |
""",
        steps="""
Luộc gà | Luộc gà với hành, gừng nướng, hầm 40 phút, vớt gà, xé phay. | 45
Nấu nước dùng | Nêm nước dùng với muối, nước mắm, tiêu. | 10
Trụng miến | Ngâm miến mềm, trụng nhanh với nước sôi. | 5
Cho nấm | Thêm nấm hương, nấm mèo vào nồi nấu 5 phút. | 5
Bày tô | Xếp miến, gà xé, nấm vào tô. | 3
Hoàn thiện | Chan nước dùng nóng, rắc hành ngò và rau răm. | 2
""",
    ),
    dict(
        title="Cao lầu Hội An",
        desc="Sợi cao lầu vàng dai, thịt xíu, tóp mỡ và rau sống, món đặc sản chỉ có ở phố cổ Hội An.",
        prep=60,
        cook=45,
        serv=4,
        lvl=3,
        nut=(520, 26, 68, 16, 3, 1100),
        ing="""
500 g | Sợi cao lầu |
400 g | Thịt heo nạc | thăn hoặc mông
2 muỗng canh | Nước tương |
2 muỗng canh | Đường |
1 muỗng canh | Ngũ vị hương |
3 tép | Tỏi | băm
50 g | Tóp mỡ | chiên giòn
200 g | Giá đỗ |
100 g | Rau sống | xà lách, húng quế, rau thơm
100 g | Bánh tráng | nướng, bẻ nhỏ
1 muỗng canh | Dầu ăn |
200 ml | Nước sốt | nước ninh thịt cô đặc
""",
        steps="""
Ướp thịt | Ướp thịt với nước tương, đường, ngũ vị hương, tỏi 30 phút. | 30
Xíu thịt | Xào săn thịt rồi đổ nước ninh 30 phút đến khi mềm, thái lát. | 40
Chuẩn bị tóp mỡ | Chiên giòn mỡ heo thái hạt lựu, vớt ráo. | 10
Chần mì | Chần sợi cao lầu, giá đỗ qua nước sôi, để ráo. | 3
Bày tô | Cho rau sống, giá, mì cao lầu, thịt xíu, tóp mỡ lên trên. | 3
Hoàn thiện | Rưới chút nước sốt xíu, rắc bánh tráng, ăn kèm ớt và rau. | 2
""",
    ),
    dict(
        title="Mì vịt tiềm",
        desc="Vịt hầm thuốc bắc mềm thơm, nước dùng đậm đà vị hồi, ăn cùng sợi mì trứng dai.",
        prep=45,
        cook=120,
        serv=4,
        lvl=3,
        nut=(620, 32, 60, 28, 3, 1250),
        ing="""
1 con | Vịt | khoảng 1.5 kg
300 g | Mì trứng |
1 gói | Thuốc bắc hầm vịt | 30g
2 quả | Hoa hồi |
1 thanh | Quế |
2 lít | Nước xương |
100 g | Nấm hương | ngâm nở
50 g | Kỷ tử |
2 muỗng canh | Nước tương |
1 muỗng canh | Đường phèn |
1 muỗng cà phê | Muối |
100 g | Cải ngọt |
""",
        steps="""
Sơ chế vịt | Làm sạch vịt, chần nước sôi có gừng, rượu. | 15
Ướp vịt | Ướp vịt với nước tương, đường, hồi, quế 30 phút. | 30
Tiềm vịt | Xếp vịt vào nồi, thêm thuốc bắc, nấm hương, đổ nước xương, tiềm 90 phút. | 90
Nêm nếm | Thêm kỷ tử, muối, đường phèn; nêm cho vừa ăn. | 5
Trụng mì | Trụng mì và cải ngọt qua nước sôi, cho vào tô. | 5
Hoàn thiện | Xếp thịt vịt lên, chan nước dùng nóng. | 3
""",
    ),
    dict(
        title="Miến xào cua",
        desc="Sợi miến dai mềm xào cùng thịt cua, giá đỗ và hẹ, đậm đà mùi tỏi phi thơm.",
        prep=30,
        cook=15,
        serv=3,
        lvl=2,
        nut=(420, 20, 58, 12, 3, 900),
        ing="""
200 g | Miến dong |
200 g | Thịt cua | tách sẵn
100 g | Giá đỗ |
100 g | Hẹ | cắt khúc
1 củ | Cà rốt | thái sợi
3 tép | Tỏi | băm
2 muỗng canh | Nước tương |
1 muỗng canh | Dầu hào |
1 muỗng cà phê | Đường |
1/2 muỗng cà phê | Tiêu |
2 muỗng canh | Dầu ăn |
1 muỗng cà phê | Dầu mè |
""",
        steps="""
Ngâm miến | Ngâm miến trong nước ấm đến khi mềm, cắt ngắn. | 15
Xào cua | Phi tỏi, xào thịt cua với chút nước tương 2 phút, xúc ra. | 4
Xào rau | Xào cà rốt, giá đỗ trong 2 phút. | 3
Xào miến | Cho miến, nước tương, dầu hào, đường vào xào 4 phút. | 5
Hoàn thiện | Thêm cua, hẹ, tiêu, dầu mè, đảo đều và dọn nóng. | 2
""",
    ),
    dict(
        title="Spaghetti sốt bò bằm",
        desc="Mì Ý al dente phủ sốt cà chua thịt bò bằm đậm vị, thêm phô mai Parmesan thơm béo.",
        prep=20,
        cook=50,
        serv=4,
        lvl=2,
        nut=(620, 32, 75, 20, 5, 900),
        ing="""
400 g | Mì Spaghetti |
400 g | Thịt bò xay |
1 củ | Hành tây | băm nhuyễn
3 tép | Tỏi | băm
400 g | Cà chua ngâm | nghiền
2 muỗng canh | Tương cà chua |
1 củ | Cà rốt | băm nhuyễn
1 muỗng cà phê | Oregano khô |
1 muỗng cà phê | Muối |
1/2 muỗng cà phê | Tiêu đen |
2 muỗng canh | Dầu ô liu |
50 g | Phô mai Parmesan |
""",
        steps="""
Phi hành tỏi | Phi thơm hành tây, tỏi, cà rốt với dầu ô liu 5 phút. | 6
Xào thịt bò | Cho thịt bò xào săn, dùng thìa dằm tơi. | 8
Nấu sốt | Đổ cà chua, tương cà, oregano, muối, tiêu; hầm lửa nhỏ 30 phút. | 30
Luộc mì | Luộc mì trong nước sôi có muối theo hướng dẫn, để ráo. | 10
Trộn mì | Trộn mì với sốt trong chảo 1 phút cho thấm. | 2
Hoàn thiện | Rắc Parmesan và ăn nóng. | 1
""",
    ),
    dict(
        title="Pizza Margherita",
        desc="Pizza kinh điển của Ý: đế mỏng giòn, sốt cà chua, mozzarella tươi và lá húng quế.",
        prep=120,
        cook=15,
        serv=3,
        lvl=3,
        nut=(520, 20, 65, 20, 3, 900),
        ing="""
300 g | Bột mì | loại số 00 hoặc đa dụng
1 muỗng cà phê | Men khô |
1 muỗng cà phê | Muối |
1 muỗng cà phê | Đường |
200 ml | Nước ấm |
2 muỗng canh | Dầu ô liu |
200 g | Cà chua ngâm | nghiền
150 g | Phô mai Mozzarella | xé miếng
1 nắm | Lá húng quế |
1 tép | Tỏi | băm
1/2 muỗng cà phê | Oregano |
1 nhúm | Tiêu đen |
""",
        steps="""
Nhào bột | Trộn bột, men, muối, đường, nước, dầu ô liu, nhào mịn 10 phút. | 10
Ủ bột | Đậy ẩm, ủ 1-1.5 giờ đến khi nở gấp đôi. | 90
Làm sốt | Trộn cà chua với tỏi, oregano, muối, tiêu. | 5
Cán đế | Chia bột, cán mỏng thành đế tròn. | 10
Xếp topping | Phết sốt, rải mozzarella. | 3
Nướng | Nướng ở 250°C khoảng 10-12 phút, thêm húng quế sau khi nướng. | 12
""",
    ),
    dict(
        title="Bít tết sốt tiêu đen",
        desc="Bò áp chảo chín tới, sốt tiêu đen kem béo và khoai tây nghiền, món chính cho bữa tiệc.",
        prep=20,
        cook=20,
        serv=2,
        lvl=2,
        nut=(650, 45, 30, 38, 4, 900),
        ing="""
2 miếng | Thăn bò | dày 3cm, khoảng 200 g/miếng
1 muỗng canh | Muối | ướp
1 muỗng cà phê | Tiêu đen | xay thô
2 muỗng canh | Dầu ô liu |
2 muỗng canh | Bơ |
3 tép | Tỏi | đập dập
2 nhánh | Hương thảo |
100 ml | Kem tươi |
50 ml | Rượu vang đỏ |
200 ml | Nước dùng bò |
2 củ | Khoai tây | luộc, nghiền
100 g | Đậu Hà Lan xanh | luộc
""",
        steps="""
Ướp bò | Để bò về nhiệt độ phòng, ướp muối, tiêu, dầu ô liu. | 20
Áp chảo | Áp chảo lửa lớn 3 phút mỗi mặt, thêm bơ, tỏi, hương thảo, tưới bơ lên thịt. | 8
Nghỉ thịt | Để bò nghỉ 5 phút cho ngấm nước. | 5
Làm sốt | Dùng chảo cũ, đổ rượu vang, nước dùng, kem, tiêu đen, sôi cho sánh. | 8
Chuẩn bị món kèm | Nghiền khoai tây với bơ, luộc đậu. | 12
Dọn ăn | Cắt bò, xếp cùng khoai, đậu, rưới sốt tiêu đen. | 3
""",
    ),
    dict(
        title="Salad Caesar gà nướng",
        desc="Xà lách romaine giòn trộn sốt Caesar béo mặn, gà áp chảo, bánh mì nướng và Parmesan.",
        prep=25,
        cook=15,
        serv=2,
        lvl=1,
        nut=(420, 34, 20, 24, 3, 850),
        ing="""
1 cây | Xà lách romaine | xé miếng
250 g | Ức gà | ướp muối tiêu
2 lát | Bánh mì | cắt hạt lựu nướng giòn
40 g | Phô mai Parmesan | bào
2 muỗng canh | Sốt Caesar |
1 muỗng canh | Dầu ô liu |
1 muỗng cà phê | Mù tạt Dijon |
1 tép | Tỏi | băm
1 quả | Chanh | vắt lấy nước
2 miếng | Cá cơm | tùy chọn
1 muỗng cà phê | Muối |
1/2 muỗng cà phê | Tiêu |
""",
        steps="""
Ướp gà | Ướp ức gà với muối, tiêu, dầu ô liu 15 phút. | 15
Áp chảo gà | Áp chảo mỗi mặt 5-6 phút đến khi chín, để nghỉ rồi thái lát. | 12
Nướng bánh mì | Nướng bánh mì viên với chút dầu tỏi đến khi giòn. | 8
Làm sốt | Trộn sốt Caesar với chanh, mù tạt, tỏi, cá cơm. | 5
Trộn salad | Trộn xà lách với sốt cho thấm đều. | 3
Hoàn thiện | Xếp gà, bánh mì, phô mai lên trên. | 2
""",
    ),
    dict(
        title="Kem trứng crème brûlée",
        desc="Kem trứng mịn mượt mùi vani, phủ lớp caramel giòn khè, gõ nhẹ muỗng là vỡ.",
        prep=20,
        cook=45,
        serv=4,
        lvl=3,
        nut=(390, 5, 28, 28, 0, 60),
        ing="""
500 ml | Kem tươi |
5 quả | Lòng đỏ trứng |
80 g | Đường cát |
1 quả | Vani | lấy hạt hoặc 1 muỗng cà phê tinh chất
1 nhúm | Muối |
4 muỗng canh | Đường | rắc mặt caramel
500 ml | Nước sôi | cách thủy
1 quả | Cam | bào vỏ, tùy chọn
1 muỗng cà phê | Rượu rum | tùy chọn
1 muỗng cà phê | Vỏ chanh bào |
1 muỗng canh | Bơ | quét khuôn
1 muỗng canh | Rượu Cointreau | tùy chọn
""",
        steps="""
Đun kem | Đun kem với vani đến khi vừa sôi lăn tăn, tắt bếp, ủ 10 phút. | 15
Trộn trứng | Đánh lòng đỏ với đường và muối đến khi sánh nhẹ. | 5
Kết hợp | Đổ từ từ kem vào lòng đỏ, khuấy đều, lọc qua rây. | 5
Đổ khuôn | Rót vào ramekin, xếp vào khay nước nóng. | 3
Nướng cách thủy | Nướng ở 150°C khoảng 35 phút đến khi rung nhẹ ở giữa. | 35
Khò đường | Để lạnh 4 giờ, rắc đường và khò caramel giòn trước khi ăn. | 240
""",
    ),
    dict(
        title="Kimbap Hàn Quốc",
        desc="Cơm cuộn rong biển nhân trứng, xúc xích, cà rốt, dưa chuột và củ cải vàng, gói gọn cho picnic.",
        prep=40,
        cook=20,
        serv=4,
        lvl=2,
        nut=(380, 14, 58, 10, 3, 800),
        ing="""
3 chén | Cơm nấu chín | dẻo, để ấm
4 tờ | Rong biển sấy |
3 quả | Trứng gà | chiên mỏng, cắt sợi
2 cây | Xúc xích | chiên
1 củ | Cà rốt | xào
1 quả | Dưa chuột | cắt sợi
4 miếng | Củ cải vàng Hàn Quốc |
1 bó | Rau chân vịt | chần, vắt ráo
1 muỗng canh | Dầu mè |
1 muỗng cà phê | Muối |
1 muỗng canh | Vừng (mè) rang |
1 muỗng canh | Giấm gạo |
""",
        steps="""
Trộn cơm | Trộn cơm với dầu mè, muối, vừng và giấm gạo. | 5
Chế biến nhân | Chiên trứng thái sợi, xào cà rốt, chần rau chân vịt, chiên xúc xích. | 15
Trải rong biển | Đặt rong biển lên mành tre, trải cơm mỏng. | 3
Xếp nhân | Xếp nhân xen kẽ ở giữa. | 3
Cuộn | Cuộn chặt nhờ mành tre, phết chút dầu mè. | 5
Cắt lát | Cắt thành khoanh vừa ăn bằng dao sắc. | 3
""",
    ),
    dict(
        title="Sushi cuộn California",
        desc="Cuộn cơm sushi trong ngoài, nhân thanh cua, bơ và dưa leo, bọc mè rang, món Nhật dễ ăn.",
        prep=45,
        cook=20,
        serv=3,
        lvl=3,
        nut=(320, 12, 55, 7, 3, 700),
        ing="""
2 chén | Gạo sushi |
3 muỗng canh | Giấm sushi |
4 tờ | Rong biển nori |
150 g | Thanh cua |
1 quả | Bơ | thái lát
1 quả | Dưa leo | thái sợi
3 muỗng canh | Vừng (mè) rang |
2 muỗng canh | Mayonnaise |
1 muỗng canh | Wasabi |
1 muỗng canh | Gừng ngâm |
100 ml | Nước tương | chấm
1 muỗng canh | Đường | trộn giấm sushi
""",
        steps="""
Nấu cơm | Nấu gạo sushi, trộn giấm sushi và để nguội. | 25
Chuẩn bị nhân | Thái bơ, dưa leo, xé thanh cua trộn mayonnaise. | 10
Trải cơm | Trải cơm ra nori, rắc mè, lật mặt cơm xuống. | 5
Cuộn | Xếp nhân lên, cuộn chặt tay bằng mành tre. | 5
Cắt lát | Cắt thành 6-8 khoanh bằng dao ướt. | 3
Thưởng thức | Ăn cùng wasabi, gừng ngâm và nước tương. | 2
""",
    ),
    dict(
        title="Pad Thái tôm",
        desc="Sợi phở gạo xào me chua ngọt cùng tôm, trứng, giá đỗ và đậu phộng, món đường phố Thái Lan.",
        prep=25,
        cook=12,
        serv=2,
        lvl=2,
        nut=(560, 24, 78, 18, 4, 1100),
        ing="""
200 g | Bánh phở khô | ngâm mềm
200 g | Tôm | bóc vỏ
2 quả | Trứng gà |
100 g | Giá đỗ |
50 g | Hẹ | cắt khúc
3 muỗng canh | Nước me |
2 muỗng canh | Nước mắm |
2 muỗng canh | Đường thốt nốt |
3 tép | Tỏi | băm
30 g | Đậu phộng rang | giã dập
1 quả | Chanh |
2 muỗng canh | Dầu ăn |
""",
        steps="""
Pha sốt | Trộn nước me, nước mắm, đường thốt nốt. | 3
Xào tôm | Phi tỏi, xào tôm đến khi chuyển màu, đẩy sang bên. | 3
Đập trứng | Đập trứng vào chảo, đảo tơi. | 2
Xào phở | Cho phở, sốt vào xào lửa lớn 3-4 phút. | 5
Cho rau | Thêm giá đỗ, hẹ, đảo nhanh 1 phút. | 1
Hoàn thiện | Rắc đậu phộng, ăn kèm chanh. | 1
""",
    ),
    dict(
        title="Tokbokki cay",
        desc="Bánh gạo dẻo sốt gochujang cay ngọt cùng chả cá và trứng luộc, món ăn vặt Hàn Quốc quen mặt.",
        prep=15,
        cook=20,
        serv=3,
        lvl=1,
        nut=(430, 12, 82, 6, 3, 1300),
        ing="""
400 g | Bánh gạo tokbokki |
150 g | Chả cá Hàn Quốc | cắt miếng
3 quả | Trứng gà | luộc chín
2 muỗng canh | Tương ớt Gochujang |
1 muỗng canh | Bột ớt Gochugaru |
2 muỗng canh | Đường |
1 muỗng canh | Nước tương |
1 muỗng canh | Tỏi băm |
500 ml | Nước dùng cá cơm |
2 nhánh | Hành lá | cắt khúc
100 g | Bắp cải | thái miếng
1 muỗng cà phê | Dầu mè |
""",
        steps="""
Ngâm bánh | Ngâm bánh gạo trong nước ấm 10 phút cho mềm. | 10
Nấu nước sốt | Đun nước dùng với gochujang, gochugaru, đường, nước tương, tỏi. | 8
Cho bánh gạo | Thả bánh gạo và bắp cải vào, đun 8-10 phút. | 10
Thêm chả cá | Cho chả cá và trứng, nấu thêm 3 phút cho sánh sốt. | 3
Hoàn thiện | Rắc hành lá, dầu mè và dọn nóng. | 1
""",
    ),
    dict(
        title="Ramen shoyu",
        desc="Ramen nước tương trong thơm, mì trứng dai, thịt chashu mềm và trứng lòng đào, ấm bụng ngày lạnh.",
        prep=45,
        cook=120,
        serv=3,
        lvl=4,
        nut=(560, 30, 62, 20, 3, 1600),
        ing="""
3 phần | Mì ramen tươi |
1 lít | Nước dùng gà |
3 muỗng canh | Nước tương Nhật |
2 muỗng canh | Mirin |
300 g | Thịt ba chỉ | cuốn chashu
3 quả | Trứng gà | luộc lòng đào
1 nắm | Giá đỗ | trụng
30 g | Măng ngâm (menma) |
3 miếng | Narutomaki | chả cá xoắn
2 nhánh | Hành lá | thái nhỏ
1 tờ | Rong biển nori | cắt miếng
1 muỗng canh | Dầu mè |
""",
        steps="""
Làm chashu | Cuộn thịt ba chỉ, buộc chặt, om với nước tương, mirin, đường 90 phút. | 90
Ướp trứng | Luộc trứng 6.5 phút, ngâm trong nước om chashu 4 giờ. | 20
Nấu nước dùng | Đun nước dùng gà, thêm nước tương và mirin nêm vừa. | 15
Trụng mì | Luộc mì 2 phút, vớt ráo. | 3
Bày tô | Cho mì, chan nước dùng, xếp chashu, trứng, măng, giá, narutomaki. | 5
Hoàn thiện | Rắc hành lá, nori, nhỏ dầu mè rồi ăn ngay. | 2
""",
    ),
]
