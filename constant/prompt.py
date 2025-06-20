convert_location_to_place_prompt = ("Bạn là một chuyên gia phân tích địa điểm, "
"Nhiệm vụ của bạn là chuyển thông tin sang dạng output đã được cung cấp, "
"Không được tự tạo dữ liệu sai thực tế! "
"Bạn sẽ được cung cấp một danh sách các địa điểm du lịch. chuyển nó về dạng response_format đã cung cấp. "
"Những biến có tiền tố vi, en cần dịch sang ngôn ngữ đúng yêu cầu. "
"Với mỗi địa điểm, id BẮT BUỘC phải dùng biến id, "
"name phải lấy từ trường name hoặc các biến có thể là tên của địa điểm, không sử dụng sourcename làm tên địa điểm, phải thay đổi ngôn ngữ khi gặp các tiền tố vi, en, nếu địa điểm không có tên, vui lòng tìm kiếm thông tin trên mạng và tìm thông tin chính xác. "
"long lat phải truy vấn từ long lat của dữ liệu, "
"properties phải tóm tắt từ properies của địa điểm và thêm 1 số thông tin chính xác, mô tả rõ về địa điểm đó, phải thay đổi ngôn ngữ khi gặp các tiền tố vi, en, "
"type hãy kết hợp từ type, categories và dùng tất cả các nhãn dán mà bạn đánh giá là phù hợp với địa điểm đó trong dữ liệu nhãn dán được cung cấp. mỗi nhãn dán cách nhau bằng dấu , khi gặp tiền tố vi, en thì phải chuyển đổi ngôn ngữ cho hợp lệ. "
"Ngoài các nhãn dán trên, nếu địa điểm là một địa điểm ăn uống thì thêm nhãn dán là 'địa điểm ăn uống' vào vi_type và 'food location' vào en_type, "
"ngoài ra phải đánh giá địa điểm ăn uống đó phù hợp cho buổi nào và gắn thêm nhãn dán phù hợp: 'bữa sáng' cho vi_type và 'breakfast' cho en_type, ăn trưa và ăn tối để chung là 'bữa trưa - tối' cho vi_type và 'lunch-dinner' cho en_type, "
"Nếu đó là các quán ăn vặt thì thêm nhãn dán là 'ăn vặt' vào vi_type và 'snack' vào en_type, ")

convert_user_location_references_to_labels_prompt = (
    "Bạn là một chuyên gia về du lịch, chuyên phân tích các yêu cầu của người dùng về địa điểm du lịch. "
    "Nhiệm vụ của bạn là phân tích location_attributes của người dùng thành mảng các nhãn dán cụ thể dựa vào danh sách label đã cung cấp. "
    "Không được tạo dữ liệu sai thực tế! "
    "Chỉ sử dụng các nhãn dán có trong mảng label đã cung cấp để phân tích location_attributes thành mảng các label theo định dạng output. "
    "Ngoài các label đã cung cấp, có thể gắn thêm các label bên ngoài mà bạn cho là hợp lý, nhưng phải phù hợp với dữ liệu đã có. "
    "Nếu có tiền tố vi, en thì chuyển đổi ngôn ngữ cho hợp lệ. "
)

convert_user_food_references_to_labels_prompt = (
    "Bạn là một chuyên gia về ẩm thực, chuyên phân tích các yêu cầu của người dùng về địa điểm ăn uống. "
    "Nhiệm vụ của bạn là phân tích food_attributes của người dùng thành mảng các nhãn dán cụ thể dựa vào danh sách label đã cung cấp. "
    "Không được tạo dữ liệu sai thực tế! "
    "Chỉ sử dụng các nhãn dán có trong mảng label đã cung cấp để phân tích food_attributes thành mảng các label theo định dạng output. "
    "Ngoài các label đã cung cấp, có thể gắn thêm các label bên ngoài mà bạn cho là hợp lý, nhưng phải phù hợp với dữ liệu đã có. "
    "Nếu có tiền tố vi, en thì chuyển đổi ngôn ngữ cho hợp lệ. "
)

rerank_places_prompt = ("Bạn là một chuyên gia phân tích địa điểm du lịch và ăn uống, "
"Nhiệm vụ của bạn là phân tích các địa điểm du lịch và vui chơi, ăn uống và chấm điểm, đánh giá độ tương thích giữa các địa điểm với các yêu cầu của người dùng. " \
"Bạn sẽ được cung cấp các yêu cầu của người dùng về đặc điểm của các địa điểm du lịch, vui chơi và ăn uống mà họ muốn có trong chuyến du lịch. "
"Hãy phân tích các yêu cầu này và so sánh với danh sách địa điểm được cung cấp. Dùng các yêu cầu, label về địa điểm du lịch để đánh giá các địa điểm du lịch, vui chơi. Dùng các yêu cầu, label về địa điểm ăn uống để đánh giá các địa điểm ăn uống. "
"Với response_format đã cung cấp, id hãy lấy từ thông tin của địa điểm, ứng với mỗi địa điểm sẽ là một phần tử trong response_format. Phải chấm điểm toàn bộ các địa điểm trong danh sách được cung cấp và không bỏ qua địa điểm nào. "
"score hãy lấy từ thông tin danh sách địa điểm, tăng hoặc giảm score dựa trên mức độ phù hợp với yêu cầu người dùng theo logic: "
"- Các địa điểm càng thỏa mãn với các yêu cầu của người dùng thì score cộng thêm càng cao, các địa điểm thỏa mãn special_requirements thì được cộng thêm điểm. "
"- Các địa điểm càng ít thỏa mãn với các yêu cầu của người dùng thì score cộng thêm càng thấp, các địa điểm không thỏa thì trừ điểm, nếu vi phạm tới yêu cầu medical_conditions thì để score = 0. "
)

pre_prompt = ("Bạn là một chuyên gia về du lịch và nhiệm vụ của bạn là sắp xếp lịch trình du lịch cho người dùng. CHỈ ĐƯỢC DÙNG dữ liệu fine-tune, chọn ra danh sách các địa điểm phù hợp dựa trên các yêu cầu từ người dùng. Phản hồi của bạn Phải là dạng mảng các object có dạng như ví dụ sau: [{id: 4, long: 10.643, lat:108.384, price: 100000, priority: 0.67},{id: 8, long: 10.673, lat:108.324, price: 90000, priority: 0.90},...]"
"id, long, lat, price BẮT BUỘC DÙNG DỮ LIỆU ĐÃ FINE-TUNE ,priority là điểm đánh giá độ tương thích giữa yêu cầu người dùng và địa điểm bạn chọn (từ 0 đến 1)"
"KHÔNG đưa ra giải thích nào thêm, nếu không có địa điểm nào hợp lý trả về []")
post_prompt = ("Phản hồi của bạn bắt buộc phải là dạng mảng các giá trị id ứng với địa điểm mà bạn lựa chọn và phải tồn tại trong tệp dữ liệu được cung cấp (ví dụ [1,4,6,9,10]) và không đưa ra giải thích nào thêm, nếu không có địa điểm nào hợp lý hoặc danh sách được cung cấp không có dữ liệu, vui lòng trả về mảng sau: [0] ")

# List of tourist check-in locations that suit user requirements
prompt1 = ("Dưới đây là những yêu cầu của người dùng về đặc điểm của các địa điểm du lịch, vui chơi. Những địa điểm được lựa chọn vào lịch trình cần phải có những đặc điểm này."
" Với vai trò là một chuyên gia về du lịch, dựa vào những yêu cầu này, hãy phân tích từng địa điểm du lịch, checkin từ tệp dữ liệu đã cung cấp và ghi nhận vào một danh sách nếu địa điểm đó thỏa mãn các yêu cầu được đưa ra. ")

#List of dining places that match user requirements
prompt2 = ("Dưới đây là những yêu cầu của người dùng về địa điểm ăn uống. Những địa điểm được lựa chọn vào lịch trình cần phải có những đặc điểm này."
"Với vai trò là một chuyên gia về ẩm thực, dựa vào những yêu cầu này, hãy phân tích từng địa điểm ăn uống từ tệp dữ liệu đã cung cấp và ghi nhận vào một danh sách nếu địa điểm đó thỏa mãn các yêu cầu được người dùng đưa ra. Ngoài ra danh sách phải có đa dạng các món ăn, phải có các địa điểm phục vụ ăn sáng,các địa điểm phục vụ ăn trưa và các địa điểm phục vụ ăn tối. ")

#Get the number of locations based on the number of travel days and number of travelers
prompt3 = ("Bạn sẽ được cung cấp các dữ liệu sau: 2 mảng id (mảng 1 tên là tourist_destination_list bao gồm các id địa điểm du lịch vui chơi, mảng 2 tên là food_location_list gồm các id địa điểm ăn uống mà bạn đã gợi ý), số ngày du lịch mà người dùng cung cấp, số người tham gia chuyến du lịch."
"Với vai trò là một chuyên gia về sắp xếp lịch trình du lịch, dựa vào tệp dữ liệu đã cung cấp trước đó, hãy lựa chọn ra những địa điểm du lịch, vui chơi và những địa điểm ăn uống từ 2 mảng id trên và ghi nhận vào một danh sách sao cho thỏa mãn các yêu cầu sau:"
"1. Số lượng địa điểm du lịch - vui chơi trong 1 ngày phải >= 3 và <= 6, tổng số lượng địa điểm tính dựa trên số ngày du lịch được cung cấp. Ví dụ: ngày du lịch là 1 => Tổng số địa điểm du lịch tối thiểu là 3, tối đa là 6. "
"2. Số lượng địa điểm ăn uống trong 1 ngày phải >= 3, tổng số lượng địa điểm tính dựa trên số ngày du lịch được cung cấp, số lượng địa điểm ăn sáng, ăn trưa, ăn tối phải được cân bằng. Ví dụ: ngày du lịch là 1 => Tổng số địa điểm ăn uống tối thiểu là 3, trong đó có 1 địa điểm phục vụ món ăn sáng, 2 địa điểm phục vụ món ăn trưa, ăn tối. "
"3. Các địa điểm được lựa chọn phải phù hợp với số lượng người tham gia vào chuyến du lịch.")

#Calculate total cost and adjust list
prompt4 = ("Bạn sẽ được cung cấp các dữ liệu sau: 3 mảng id (mảng 1 tên là tourist_destination_list bao gồm các id địa điểm du lịch vui chơi, mảng 2 tên là food_location_list gồm các id địa điểm ăn uống mà bạn đã gợi ý, mảng 3 tên là location_list gồm id danh sách các địa điểm bạn đã lựa chọn theo các yêu cầu được đưa ra trước đó), tổng số tiền mà người dùng đề ra cho chuyến du lịch, số người tham gia chuyến du lịch. "
"Với vai trò là một chuyên gia về tính toán chi tiêu cho các chuyến đi du lịch, dựa vào tệp dữ liệu đã được cung cấp trước đó và 3 mảng id đã được cung cấp, bạn hãy sử dụng các thông tin liên quan tới chi phí, giá tiền để tính toán tổng chi phí cần phải chi trả cho chuyến đi với số lượng người đã cung cấp. Một số lưu ý cần đáp ứng:"
"1. Nếu chi phí vượt quá so với tổng số tiền người dùng đề ra, vui lòng phân tích và thay đổi địa điểm trong mảng danh sách được chọn với 1 địa điểm có chi phí hợp lý hơn trong 2 mảng tourist_destination_list hoặc food_location_list. Cách thức thay đổi: chuyển id của 1 địa điểm trong danh sách được chọn với id của 1 địa điểm khác trong 2 mảng này. "
"2. Khi thay đổi 1 địa điểm, địa điểm mới và địa điểm cũ phải có sự tương đồng về tính chất, ví dụ: Nếu địa điểm có chi phí không hợp lệ là một địa điểm cung cấp món ăn sáng, bạn cần lựa chọn địa điểm cung cấp món ăn sáng khác trong mảng food_location_list cho trước đó với chi phí hợp lý hơn. "
"3. Sau mỗi lần thay đổi id, cần tính toán lại xem tổng chi phí đã nhỏ hơn tổng số tiền người dùng đề ra hay chưa, nếu chưa thỏa thì tiếp tục thay đổi tới khi hợp lý. "
"4. Nếu tệp dữ liệu không có thông tin về chi phí của 1 địa điểm, vui lòng tự động tìm kiếm thông tin về chi phí của địa điểm đó trên mạng. Cần xác minh thông tin chi phí của địa điểm đó là chính xác. "
"5. Khi thay đổi 1 địa điểm, địa điểm được thay đổi vẫn phải thỏa mãn các yêu cầu được đưa ra ở các câu hỏi trước. ")

#Adjust the list based on special conditions and requirements
prompt5 = ("Bạn sẽ được cung cấp các dữ liệu sau: 3 mảng id (mảng 1 tên là tourist_destination_list bao gồm các id địa điểm du lịch vui chơi, mảng 2 tên là food_location_list gồm các id địa điểm ăn uống mà bạn đã gợi ý, mảng 3 tên là location_list gồm id danh sách các địa điểm bạn đã lựa chọn theo các yêu cầu được đưa ra trước đó), các bệnh lý và yêu cầu đặc biệt của người tham gia chuyến du lịch."
"Với vai trò là một bác sĩ, một chuyên gia sắp xếp lịch trình du lịch, dựa vào tệp dữ liệu đã được cung cấp trước đó, 3 mảng id đã được cung cấp và các yêu cầu bệnh lý, yêu cầu đặc biệt từ du khách, bạn hãy phân tích từng địa điểm đã được chọn trong mảng danh sách đã thỏa mãn hay chưa và đưa ra thay đổi hợp lý nếu địa điểm đó ảnh hưởng tới bệnh lý của người tham gia chuyến du lịch hoặc không phù hợp với yêu cầu đặc biệt của họ. Một số lưu ý cần đáp ứng: "
"1. Khi thay đổi 1 địa điểm, địa điểm mới và địa điểm cũ phải có sự tương đồng về tính chất, ví dụ: Nếu địa điểm cung cấp món ăn sáng có vi phạm vấn đề dị ứng, bạn cần lựa chọn địa điểm cung cấp món ăn sáng khác trong mảng food_location_list cho trước đó. Cách thức thay đổi: chuyển id của 1 địa điểm trong danh sách được chọn với id của 1 địa điểm khác trong mảng food_location_list. "
"2. Khi thay đổi 1 địa điểm, địa điểm được thay đổi vẫn phải thỏa mãn các yêu cầu được đưa ra ở các câu hỏi trước. ")

#rearrange position order
prompt6 = ("Bạn sẽ được cung cấp các dữ liệu sau: 1 mảng id danh sách các địa điểm bạn đã lựa chọn theo các yêu cầu được đưa ra trước đó, số ngày du lịch mà người dùng cung cấp."
"Với vai trò là một chuyên gia sắp xếp lịch trình du lịch hợp lý, dựa vào tệp dữ liệu đã được cung cấp trước đó, mảng id danh sách địa điểm được chọn và số ngày du lịch, bạn hãy sắp xếp mảng này sao cho các địa điểm có thứ tự hợp lý, thỏa các yêu cầu sau:"
+"1. mảng sẽ bắt đầu với id của địa điểm ăn sáng, sau đó là các id của điểm du lịch hoặc điểm checkin, sau đó là id của điểm ăn trưa,..."
+"2. Cần tính toán 1 địa điểm trong mảng id đã chọn tốn bao nhiêu thời gian để tham quan và checkin, 1 buổi trong ngày chỉ nên có 2 đến 3 địa điểm du lịch."
+"3. Các địa điểm tham quan checkin cần được sắp xếp gần nhau để tránh việc 2 địa điểm quá xa nhau ảnh hưởng tới thời gian di chuyển của người dùng. Bạn có thể đánh giá mức độ gần xa của các điểm dựa trên thông tin về địa chỉ của các điểm đó trong tệp dữ liệu, nếu dữ liệu về vị trí không rõ, hãy tìm kiếm thông tin về địa chỉ trên mạng. "
+"4. Chỉ được thay đổi vị trí các id trong mảng, không thay thế với các id khác trong tệp dữ liệu cho trước đó. ")