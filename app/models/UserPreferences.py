class UserPreferences:
    def __init__(self, num_days, budget, slots, location_attributes, food_attributes, special_requirements, medical_conditions):
        self.num_days = num_days
        self.budget = budget
        self.slots = slots
        self.location_attributes = location_attributes
        self.food_attributes = food_attributes
        self.special_requirements = special_requirements
        self.medical_conditions = medical_conditions

    def to_string(self):
        return (f"Người dùng muốn đi du lịch {self.days} ngày với ngân sách {self.total:,} VND, "
                f"số lượng người tham gia là {self.slots} người. Họ thích các địa điểm {self.location_type}. "
                f"Yêu cầu đặc biệt: {self.special_requires}. "
                f"Tình trạng sức khỏe: {self.health_conditions}.")
    def get_days(self):
        return (f"Số ngày du lịch: {self.days}")
    def get_budget(self):
        return (f"Ngân sách cho chuyến du lịch: {self.budget} VND")
    def get_slots(self):
        return (f"Số lượng người tham gia: {self.slots} người")
    def get_location_attributes(self):
        return (f"Các đặc điểm của địa điểm mà người dùng yêu cầu: {self.location_attributes}")
    def get_food_attributes(self):
        return (f"Các đặc điểm của món ăn, thức uống mà người dùng yêu cầu: {self.food_attributes}")
    def get_special_requirements(self):
        return (f"Yêu cầu đặc biệt của người dùng: {self.special_requirements}")
    def get_medical_conditions(self):
        return (f"Tình trạng sức khoẻ của người dùng: {self.medical_conditions}")
    

    