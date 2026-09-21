"""Seed catalogue: category -> [(recipe title, Wikimedia Commons search queries tried in order)]."""

CATALOGUE: list[tuple[str, list[tuple[str, list[str]]]]] = [
    (
        "Phở và bún nước",
        [
            ("Phở bò Hà Nội", ["Phở bò", "pho bo Vietnamese noodle soup"]),
            ("Bún bò Huế", ["Bún bò Huế", "bun bo Hue"]),
            ("Bún riêu cua", ["Bún riêu", "bun rieu cua"]),
            ("Hủ tiếu Nam Vang", ["Hủ tiếu", "hu tieu Nam Vang"]),
            ("Bún chả cá Nha Trang", ["Bún chả cá", "bun cha ca"]),
        ],
    ),
    (
        "Món cuốn và gỏi",
        [
            ("Gỏi cuốn tôm thịt", ["Gỏi cuốn", "goi cuon spring rolls Vietnam"]),
            ("Bánh cuốn nóng Thanh Trì", ["Bánh cuốn", "banh cuon"]),
            ("Gỏi đu đủ khô bò", ["Gỏi đu đủ khô bò", "Gỏi đu đủ"]),
            ("Nem nướng Nha Trang", ["Nem nướng", "nem nuong"]),
            ("Gỏi xa lát cải tím", ["Gỏi xa lát"]),
        ],
    ),
    (
        "Cơm",
        [
            ("Cơm tấm sườn bì chả", ["Cơm tấm", "com tam suon"]),
            ("Cơm cháy chà bông", ["Cơm cháy"]),
            ("Cơm lam Tây Nguyên", ["Cơm lam"]),
            ("Cơm niêu Huế", ["Cơm niêu"]),
            ("Cơm bò xào cần tỏi", ["Cơm Bò Xào"]),
        ],
    ),
    (
        "Bánh mặn",
        [
            ("Bánh mì thịt nướng", ["Bánh mì", "banh mi sandwich"]),
            ("Bánh xèo miền Tây", ["Bánh xèo", "banh xeo"]),
            ("Bánh khọt Vũng Tàu", ["Bánh khọt", "banh khot"]),
            ("Bánh bèo Huế", ["Bánh bèo", "banh beo"]),
            ("Bánh bột lọc", ["Bánh bột lọc", "banh bot loc"]),
        ],
    ),
    (
        "Món kho",
        [
            ("Thịt kho tàu", ["Thịt kho tàu", "thit kho Vietnamese braised pork eggs"]),
            ("Cá kho tộ", ["Cá kho tộ", "ca kho to Vietnamese caramelized fish"]),
            ("Gà kho sả", ["Gà kho"]),
            ("Sườn non kho khóm", ["Sườn kho", "Vietnamese braised pork ribs"]),
            ("Bò kho bánh mì", ["Bò kho"]),
        ],
    ),
    (
        "Món xào",
        [
            ("Rau muống xào tỏi", ["Rau muống xào tỏi", "stir fried water spinach garlic"]),
            ("Bò lúc lắc", ["Bò lúc lắc", "shaking beef Vietnamese"]),
            ("Ốc xào rau muống", ["Ốc xào rau muống"]),
            ("Bò xào hành tây", ["Bò xào", "stir fried beef onion"]),
            ("Phở xào bò", ["Phở xào"]),
        ],
    ),
    (
        "Canh và súp",
        [
            ("Canh chua cá lóc", ["Canh chua", "canh chua ca Vietnamese sour soup"]),
            ("Canh khổ qua nhồi thịt", ["Canh khổ qua", "stuffed bitter melon soup"]),
            ("Súp cua trứng bắc thảo", ["Súp cua", "crab soup Vietnamese"]),
            ("Canh bí đao nấu tôm", ["Canh bí đao", "winter melon soup"]),
            ("Canh bắp cải cuộn thịt", ["Canh bap cai cuon thit"]),
        ],
    ),
    (
        "Món nướng",
        [
            ("Thịt heo nướng sả", ["Thịt nướng", "Vietnamese grilled pork lemongrass"]),
            ("Chả cá Lã Vọng", ["Chả cá Lã Vọng", "cha ca La Vong"]),
            ("Bò nướng lá lốt", ["Bò lá lốt", "bo la lot grilled beef betel leaf"]),
            ("Gà nướng mật ong", ["Honey glazed roast chicken", "grilled chicken honey"]),
            ("Cá lóc nướng trui", ["Cá lóc nướng", "grilled snakehead fish Vietnam"]),
        ],
    ),
    (
        "Món chiên và rán",
        [
            ("Chả giò rế", ["Chả giò", "cha gio fried spring rolls"]),
            ("Cánh gà chiên nước mắm", ["Cánh gà chiên nước mắm", "fish sauce chicken wings"]),
            ("Cá nục rán chảo", ["Cá nục rán"]),
            ("Đậu hũ chiên sả ớt", ["Đậu hũ chiên", "fried tofu lemongrass"]),
            ("Bánh tôm Hồ Tây", ["Bánh tôm"]),
        ],
    ),
    (
        "Lẩu",
        [
            ("Lẩu hải sản", ["Lẩu hải sản"]),
            ("Lẩu mì hải sản", ["Lẩu mì hải sản"]),
            ("Lẩu bò", ["Lẩu bò"]),
            ("Lẩu cá dày", ["Lẩu cá dày"]),
            ("Lẩu nấm", ["Lẩu nấm", "Lẩu mì"]),
        ],
    ),
    (
        "Món chay",
        [
            ("Đậu hũ sốt cà chua", ["Đậu hũ sốt cà", "tofu tomato sauce"]),
            ("Bánh đúc lạc chay", ["Bánh đúc lạc", "Bánh đúc"]),
            ("Bánh bao chay nhân nấm", ["Bánh bao"]),
            ("Cơm chiên chay", ["Cơm chay", "Vietnamese vegetarian rice"]),
            ("Chả giò chay", ["Chả giò chay", "vegetarian spring rolls"]),
        ],
    ),
    (
        "Hải sản",
        [
            ("Cua rang muối", ["Cua rang muối"]),
            ("Mực hấp gừng", ["Mực hấp", "steamed squid ginger"]),
            ("Ốc hương rang me", ["Ốc hương"]),
            ("Sò điệp nướng mỡ hành", ["Sò điệp nướng", "grilled scallops scallion oil"]),
            ("Tôm nướng muối ớt", ["Tôm nướng", "grilled prawns chili salt"]),
        ],
    ),
    (
        "Chè và tráng miệng",
        [
            ("Chè chuối chưng", ["Chè chuối"]),
            ("Chè đậu xanh", ["Chè đậu xanh", "mung bean sweet soup"]),
            ("Chè đậu đen", ["Chè đậu đen"]),
            ("Chè khúc bạch", ["Chè khúc bạch", "khuc bach dessert"]),
            ("Bánh rán ngọt", ["Bánh rán"]),
        ],
    ),
    (
        "Bánh ngọt truyền thống",
        [
            ("Bánh flan caramel", ["Bánh flan", "caramel flan"]),
            ("Bánh đậu xanh Hải Dương", ["Bánh đậu xanh"]),
            ("Bánh da lợn", ["Bánh da lợn", "banh da lon"]),
            ("Bánh bò hấp", ["Bánh bò", "banh bo steamed cake"]),
            ("Bánh tét nhân đậu xanh", ["Bánh tét", "banh tet"]),
        ],
    ),
    (
        "Đồ uống",
        [
            ("Cà phê sữa đá", ["Cà phê sữa đá", "Vietnamese iced coffee"]),
            ("Cà phê trứng Hà Nội", ["Cà phê trứng", "egg coffee"]),
            ("Sinh tố bơ", ["Sinh tố bơ", "avocado smoothie"]),
            ("Nước mía tắc", ["Nước mía", "sugarcane juice"]),
            ("Cà phê muối Huế", ["Cà Phê Muối"]),
        ],
    ),
    (
        "Món ăn kèm và dưa muối",
        [
            ("Mắm tôm pha chanh đường", ["Mắm tôm"]),
            ("Dưa cải muối chua", ["Dưa cải muối", "pickled mustard greens"]),
            ("Dưa muối xổi", ["Dưa muối"]),
            ("Đồ chua cà rốt củ cải", ["Đồ chua", "do chua pickled carrot daikon"]),
            ("Nem chua Thanh Hóa", ["Nem chua"]),
        ],
    ),
    (
        "Xôi và cháo",
        [
            ("Xôi gấc", ["Xôi gấc", "xoi gac"]),
            ("Xôi xéo", ["Xôi xéo", "xoi xeo"]),
            ("Cháo lòng", ["Cháo lòng", "chao long"]),
            ("Cháo gà hành gừng", ["Cháo gà", "Vietnamese chicken porridge"]),
            ("Xôi ngũ sắc", ["Xôi ngũ sắc"]),
        ],
    ),
    (
        "Mì và miến",
        [
            ("Mì Quảng", ["Mì Quảng", "mi quang"]),
            ("Miến gà", ["Miến gà", "mien ga glass noodle chicken soup"]),
            ("Cao lầu Hội An", ["Cao lầu", "cao lau Hoi An"]),
            ("Mì vịt tiềm", ["Mì vịt tiềm"]),
            ("Miến xào cua", ["Miến xào", "stir fried glass noodles"]),
        ],
    ),
    (
        "Món Âu",
        [
            ("Spaghetti sốt bò bằm", ["Spaghetti Bolognese", "spaghetti bolognese"]),
            ("Pizza Margherita", ["Pizza Margherita", "margherita pizza"]),
            ("Bít tết sốt tiêu đen", ["Steak black pepper sauce", "beef steak"]),
            ("Salad Caesar gà nướng", ["Caesar salad", "chicken caesar salad"]),
            ("Kem trứng crème brûlée", ["Crème brûlée", "creme brulee"]),
        ],
    ),
    (
        "Món Á",
        [
            ("Kimbap Hàn Quốc", ["Kimbap", "gimbap"]),
            ("Sushi cuộn California", ["California roll", "sushi rolls"]),
            ("Pad Thái tôm", ["Pad Thai", "pad thai shrimp"]),
            ("Tokbokki cay", ["Tteokbokki", "tteokbokki"]),
            ("Ramen shoyu", ["Shoyu ramen", "ramen noodles"]),
        ],
    ),
]
