from itertools import product, permutations

# Danh sách bữa ăn kèm priority
an_sang = [("as1", 0.6), ("as2", 0.4)]
an_trua = [("atr1", 0.3), ("atr2", 0.7)]
an_toi = [("at1", 0.5), ("at2", 0.2), ("at3", 0.6), ("at4", 0.3)]

# Danh sách địa điểm du lịch kèm priority
du_lich = [("dl1", 0.8), ("dl2", 0.6), ("dl3", 0.3), ("dl4", 0.5)]

# Ngưỡng tổng priority tối đa
priority_threshold = 3.5

# Tạo tất cả tổ hợp của bữa ăn
meal_combinations = product(an_sang, an_trua, an_toi)

# Lưu kết quả hợp lệ
valid_results = []

# Duyệt từng tổ hợp bữa ăn
for (meal_sang, pri_sang), (meal_trua, pri_trua), (meal_toi, pri_toi) in meal_combinations:
    # Lấy tất cả tổ hợp 4 địa điểm du lịch không trùng nhau
    for (dl1, pri_dl1), (dl2, pri_dl2), (dl3, pri_dl3), (dl4, pri_dl4) in permutations(du_lich, 4):
        # Tạo danh sách kế hoạch
        structured_list = [meal_sang, dl1, dl2, meal_trua, dl3, dl4, meal_toi]
        
        # Tính tổng priority
        total_priority = pri_sang + pri_dl1 + pri_dl2 + pri_trua + pri_dl3 + pri_dl4 + pri_toi
        
        # Nếu tổng priority ≤ 3.5 thì thêm vào danh sách hợp lệ
        if total_priority >= priority_threshold:
            valid_results.append(structured_list)

# In thử 5 kết quả đầu tiên
for result in valid_results[:-1]:
    print(result)
