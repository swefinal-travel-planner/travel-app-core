LABEL = '''commercial,catering,spa,tourism,entertainment,historic,supermarket,marketplace,shopping_mall,department_store,outdoor_and_sport,hobby,books,gift_and_souvenir,stationery,clothing,garden,florist,bakery,deli,pasta,ice_cream,seafood,fruit_and_vegetable,farm,confectionery,chocolate,drinks,coffee_and_tea,discount_store,jewelry,watches,art,antiques,trade,kiosk,restaurant,cafe,bar,pub,ice_cream,biergarten,taproom,education.library,culture,culture.theatre,culture.arts_centre,culture.gallery,zoo,aquarium,museum,cinema,amusement_arcade,escape_game,miniature_golf,bowling_alley,flying_fox,theme_park,water_park,activity_park,heritage.unesco,picnic,playground,spa,spa.public_bath,spa.sauna,park,forest,water,water.spring,water.reef,water.hot_spring,water.sea,mountain,mountain.peak,mountain.cave_entrance,sand,protected_area,national_park,service.beauty.spa,service.beauty.massage,attraction,sights,place_of_worship,monastery,city_hall,lighthouse,windmill,tower,battlefield,fort,castle,ruines,archaeological_site,city_gate,bridge,memorial,camp_pitch,camp_site,summer_camp,caravan_site,beach.beach_resort,nightclub,casino,adult_gaming_centre,viewpoint,information,trailhead,winery,brewery,distillery,farm_experience,vineyard,photospot,sunset_point,cultural_experience,local_market,handicraft_village,floating_market,night_market,boat_tour,hiking_route,bike_tour,eco_tourism,street_food,food_court,local_cuisine,fine_dining,buffet,hot_pot,bbq,seafood_restaurant,vegetarian,vegan,fast_food,food_truck,teahouse,dessert_shop,noodle_shop,sushi_bar,korean_bbq,ramen,craft_beer'''

en_labels = {
    "Shopping": [
        "commercial", "supermarket", "marketplace", "shopping_mall", "department_store",
        "outdoor_and_sport", "hobby", "books", "gift_and_souvenir", "stationery",
        "clothing", "garden", "florist", "discount_store", "jewelry", "watches",
        "art", "antiques", "trade", "kiosk"
    ],
    "Food & Drink": [
        "bakery", "deli", "pasta", "ice_cream", "seafood", "fruit_and_vegetable",
        "farm", "confectionery", "chocolate", "drinks", "coffee_and_tea",
        "restaurant", "cafe", "bar", "pub", "biergarten", "taproom",
        "street_food", "food_court", "local_cuisine", "fine_dining", "buffet",
        "hot_pot", "bbq", "seafood_restaurant", "vegetarian", "vegan", "fast_food",
        "food_truck", "teahouse", "dessert_shop", "noodle_shop", "sushi_bar",
        "korean_bbq", "ramen", "craft_beer"
    ],
    "Spa & Wellness": [
        "spa", "public_bath", "sauna", "massage"
    ],
    "Nature": [
        "park", "forest", "spring", "reef",
        "hot_spring", "sea", "mountain", "peak",
        "cave_entrance", "sand", "protected_area", "national_park"
    ],
    "Outdoor Activities": [
        "picnic", "playground", "viewpoint", "trailhead", "hiking_route",
        "bike_tour", "eco_tourism", "farm_experience", "vineyard",
        "photospot", "sunset_point"
    ],
    "Entertainment": [
        "entertainment", "zoo", "aquarium", "museum", "cinema",
        "amusement_arcade", "escape_game", "miniature_golf",
        "bowling_alley", "flying_fox", "theme_park", "water_park",
        "activity_park", "nightclub", "casino", "adult_gaming_centre"
    ],
    "Culture & Arts": [
        "library", "culture", "theatre", "arts_centre",
        "gallery", "cultural_experience"
    ],
    "History & Landmarks": [
        "historic", "heritage.unesco", "sights", "attraction",
        "place_of_worship", "monastery", "city_hall", "lighthouse",
        "windmill", "tower", "battlefield", "fort", "castle", "ruines",
        "archaeological_site", "city_gate", "bridge", "memorial"
    ],
    "Camping & Resort": [
        "camp_pitch", "camp_site", "summer_camp", "caravan_site",
        "beach.beach_resort"
    ],
    "Tourism Services": [
        "tourism", "boat_tour", "winery", "brewery", "distillery",
        "local_market", "handicraft_village", "floating_market",
        "night_market"
    ]
}

vi_labels = {
    "Mua Sắm": [
        "thương mại", "siêu thị", "chợ", "trung tâm mua sắm", "cửa hàng tổng hợp",
        "ngoài trời & thể thao", "sở thích", "sách", "quà lưu niệm", "văn phòng phẩm",
        "quần áo", "vườn", "cửa hàng hoa", "cửa hàng giảm giá", "trang sức", "đồng hồ",
        "nghệ thuật", "đồ cổ", "buôn bán", "quầy hàng"
    ],
    "Thực Phẩm & Đồ Uống": [
        "tiệm bánh", "cửa hàng thịt nguội", "mì ống", "kem", "hải sản", "rau củ quả",
        "nông trại", "bánh kẹo", "sô cô la", "đồ uống", "cà phê & trà",
        "nhà hàng", "quán cà phê", "quán bar", "quán rượu", "vườn bia", "taproom",
        "đồ ăn đường phố", "khu ẩm thực", "ẩm thực địa phương", "ẩm thực cao cấp", "buffet",
        "lẩu", "bbq", "nhà hàng hải sản", "chay", "thuần chay", "đồ ăn nhanh",
        "xe đồ ăn", "quán trà", "tiệm tráng miệng", "quán mì", "quán sushi",
        "nướng Hàn Quốc", "ramen", "bia thủ công"
    ],
    "Thư Giãn & Làm Đẹp": [
        "spa", "nhà tắm công cộng", "xông hơi", "massage"
    ],
    "Thiên Nhiên": [
        "công viên", "khu rừng", "suối", "rạn san hô",
        "suối nước nóng", "biển", "núi", "đỉnh núi",
        "cửa hang", "bãi cát", "khu bảo tồn", "vườn quốc gia"
    ],
    "Hoạt Động Ngoài Trời": [
        "dã ngoại", "sân chơi", "điểm ngắm cảnh", "đầu đường mòn", "tuyến đi bộ",
        "tour xe đạp", "du lịch sinh thái", "trải nghiệm nông trại", "vườn nho",
        "điểm chụp hình", "điểm ngắm hoàng hôn"
    ],
    "Giải Trí": [
        "giải trí", "vườn thú", "thủy cung", "bảo tàng", "rạp chiếu phim",
        "khu trò chơi", "trò chơi thoát hiểm", "golf mini",
        "bowling", "đu dây mạo hiểm", "công viên giải trí", "công viên nước",
        "công viên hoạt động", "hộp đêm", "sòng bạc", "trung tâm trò chơi người lớn"
    ],
    "Văn Hóa & Nghệ Thuật": [
        "thư viện", "văn hóa", "nhà hát", "trung tâm nghệ thuật",
        "phòng trưng bày", "trải nghiệm văn hóa"
    ],
    "Lịch Sử & Di Tích": [
        "lịch sử", "di sản unesco", "cảnh đẹp", "điểm thu hút",
        "nơi thờ tự", "tu viện", "tòa thị chính", "hải đăng",
        "cối xay gió", "tháp", "chiến trường", "pháo đài", "lâu đài", "di tích",
        "khu khảo cổ", "cổng thành", "cầu", "tượng đài"
    ],
    "Cắm Trại & Khu Nghỉ Dưỡng": [
        "bãi cắm trại", "khu cắm trại", "trại hè", "khu caravan",
        "khu nghỉ dưỡng bãi biển"
    ],
    "Dịch Vụ Du Lịch": [
        "du lịch", "tour thuyền", "nhà máy rượu vang", "nhà máy bia", "xưởng chưng cất",
        "chợ địa phương", "làng nghề", "chợ nổi",
        "chợ đêm"
    ]
}

def format_label(label):
    # Chuyển snake_case hoặc dot.case sang dạng có dấu cách và viết hoa chữ cái đầu mỗi từ
    return ' '.join([w.capitalize() for w in label.replace('.', ' ').replace('_', ' ').split()])

def format_label_vi(label):
    # Viết hoa chữ cái đầu mỗi từ, giữ nguyên dấu tiếng Việt
    return ' '.join([w.capitalize() for w in label.split()])

def get_en_labels():
    return {key: [format_label(label) for label in labels] for key, labels in en_labels.items()}

def get_vi_labels():
    return {key: [format_label_vi(label) for label in labels] for key, labels in vi_labels.items()}

def normalize_label_vi(label):
    # Chuyển "Du Lịch" thành "du lịch"
    return label.strip().lower()

def normalize_label_en(label):
    # Chuyển "Discount Store" thành "discount_store"
    return label.strip().lower().replace(' ', '_')
