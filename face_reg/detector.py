import cv2
import face_recognition
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime,time,timedelta
from zoneinfo import ZoneInfo


# Hàm lấy thông tin người dùng từ cơ sở dữ liệu
def getProfile(id):
    try:
        conn = sqlite3.connect("FaceBase.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM People WHERE ID=?", (id,))
        profile = cursor.fetchone()
        return profile
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

# Hàm lấy tất cả mã nhận diện khuôn mặt từ cơ sở dữ liệu
def getAllFaceEncodings():
    try:
        conn = sqlite3.connect("FaceBase.db")
        cmd = "SELECT ID, Encoding FROM FaceEncodings"
        cursor = conn.execute(cmd)
        face_encodings = {}
        for row in cursor:
            id = row[0]
            encoding = np.frombuffer(row[1], dtype=np.float64)  # Chuyển đổi nhị phân sang numpy array
            face_encodings[id] = encoding
        return face_encodings
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {}
    finally:
        conn.close()


from datetime import datetime

def recordOrUpdateTime(Id, db_path="FaceBase.db"):
    now_time = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    current_time = now_time.time()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Kiểm tra xem ID có tồn tại trong bảng và có dữ liệu ở cột ThờiGianVàoLớp chưa
    cursor.execute("SELECT ThờiGianVàoLớp FROM People WHERE ID=?", (Id,))
    record = cursor.fetchone()

    if record is None:  # ID chưa tồn tại
        print(f"ID {Id} chưa tồn tại trong bảng.")
        conn.close()
        return

    old_time = record[0]  # Giá trị của cột ThờiGianVàoLớp
    print(old_time)
    if old_time is None:  # Chưa có dữ liệu ở cột ThờiGianVàoLớp
        # Thêm thời gian hiện tại vào cột ThờiGianVàoLớp
        cursor.execute("UPDATE People SET ThờiGianVàoLớp=? WHERE ID=?", (now_time, Id))
        cursor.execute("UPDATE People SET VÀORA =? WHERE ID=?", ('vào', Id))

        if vo_tiet_1 <= current_time <= ra_tiet_1:
            cursor.execute("UPDATE People SET TrạngThái =? WHERE ID=?", ('trễ', Id))
        elif vo_tiet_2 <= current_time <= ra_tiet_2:
            cursor.execute("UPDATE People SET TrạngThái =? WHERE ID=?", ('Bỏ tiết 1', Id))
        elif vo_tiet_3 <= current_time <= ra_tiet_3:
            cursor.execute("UPDATE People SET TrạngThái =? WHERE ID=?", ('Bỏ tiết 1,2', Id))
        elif vo_tiet_4 <= current_time <= ra_tiet_4:
            cursor.execute("UPDATE People SET TrạngThái =? WHERE ID=?", ('Bỏ tiết 1,2,3', Id))
        elif vo_tiet_5 <= current_time <= ra_tiet_5:
            cursor.execute("UPDATE People SET TrạngThái =? WHERE ID=?", ('Bỏ tiết 1,2,3,4', Id))
        else:
            cursor.execute("UPDATE People SET TrạngThái =? WHERE ID=?", ('vắng học', Id))
        
        conn.commit()
        print(f"Thời gian được cập nhật cho ID {Id}: {now_time}")
    else:  # Đã có dữ liệu trong cột ThờiGianVàoLớp
        try:
            # Nếu now_time là datetime, chuyển nó thành chuỗi ISO trước
            if isinstance(now_time, datetime):
                now_time = now_time.isoformat()  # Chuyển thành chuỗi ISO 8601

            # Chuyển đổi thời gian cũ và thời gian hiện tại thành đối tượng datetime bao gồm múi giờ
            old_time_obj = datetime.fromisoformat(old_time)
            now_time_obj = datetime.fromisoformat(now_time)

            # Kiểm tra sự chênh lệch thời gian
            time_difference = (now_time_obj - old_time_obj).total_seconds() / 60  # Tính theo phút
            if time_difference > 1:  # Chênh lệch lớn hơn 1 phút
                cursor.execute("UPDATE People SET ThờiGianVàoLớp=? WHERE ID=?", (now_time, Id))
                
                cursor.execute("SELECT VÀORA FROM People WHERE ID=?", (Id,))
                vao_ra_value = cursor.fetchone()[0]
                
                if vao_ra_value == 'ra':
                    cursor.execute("UPDATE People SET VÀORA =? WHERE ID=?", ('vào', Id))
                else:
                    cursor.execute("UPDATE People SET VÀORA =? WHERE ID=?", ('ra', Id))

                conn.commit()
                
                print(f"Đã cập nhật thời gian mới cho ID {Id}: {now_time}")
            else:
                print(f"Thời gian hiện tại không đủ chênh lệch để cập nhật (chỉ {time_difference:.2f} phút).")
        except ValueError as e:
            pass

    conn.close()


# Khởi tạo camera
cam = cv2.VideoCapture('http://192.168.1.2:8080/video')
if not cam.isOpened():
    print("Unable to connect to the camera. Please check the IP or network.")
    exit()

# Lấy tất cả các mã nhận diện đã lưu
known_face_encodings = getAllFaceEncodings()

# Biến đếm khung hình để giảm tải xử lý
frame_skip = 5
frame_counter = 0

# Tạo một danh sách để lưu ID và tên
recognized_ids = set()
recognized_faces = []


vo_tiet_1, ra_tiet_1 = time(7 ,15), time(8 , 0)
vo_tiet_2, ra_tiet_2 = time(8 , 5), time(8 ,50)
vo_tiet_3, ra_tiet_3 = time(8 ,55), time(9 ,40)
vo_tiet_4, ra_tiet_4 = time(9 ,55), time(10,40)
vo_tiet_5, ra_tiet_5 = time(10,45), time(11,30)



while True:
    # Đọc ảnh từ camera
    ret, img = cam.read()
    if not ret:
        print("Failed to grab frame.")
        break

    frame_counter += 1
    if frame_counter % frame_skip != 0:
        continue

    img = cv2.resize(img, (600, 400))  # Thay đổi kích thước để giảm tải
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Chuyển sang RGB cho face_recognition

    # Phát hiện khuôn mặt
    face_locations = face_recognition.face_locations(rgb_img)
    face_encodings = face_recognition.face_encodings(rgb_img, face_locations)

    # Xử lý từng khuôn mặt
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(list(known_face_encodings.values()), face_encoding)
        face_distances = face_recognition.face_distance(list(known_face_encodings.values()), face_encoding)

        if any(matches):
            best_match_index = np.argmin(face_distances)  # Lấy khoảng cách nhỏ nhất
            matched_id = list(known_face_encodings.keys())[best_match_index]
            profile = getProfile(matched_id)

            if profile:
                recordOrUpdateTime(matched_id, db_path="FaceBase.db")
                id_to_display = f"ID: {profile['ID']}"
                name_to_display = f"Name: {profile['Name']}"
                lop_to_display = f"LOP: {profile['LOP']}"
                cv2.putText(img, id_to_display, (left, bottom + 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(img, lop_to_display, (left, bottom + 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            
            else:
                name_to_display = "Unknown"
        else:
            name_to_display = "Unknown"

        # Hiển thị tên
        cv2.putText(img, name_to_display, (left, bottom + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.rectangle(img, (left, top), (right, bottom), (255, 0, 0), 2)


    # Hiển thị khung hình
    cv2.imshow('Face Recognition', img)

    # Nhấn 'q' để thoát
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


def write_to_csv(db_path="FaceBase.db", output_file="quanlyhocsinh.csv"):
    try:
        # Kết nối với cơ sở dữ liệu
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Truy vấn dữ liệu từ bảng People
        cursor.execute("""
            SELECT ID, Name, LOP, ThờiGianVàoLớp, TrạngThái
            FROM People
            WHERE ThờiGianVàoLớp IS NOT NULL
        """)
        rows = cursor.fetchall()

        # Định nghĩa tiêu đề cột
        column_names = ["ID", "Tên", "Lớp", "Thời gian vào lớp", "Trạng thái"]

        # Chuyển dữ liệu thành DataFrame
        data = pd.DataFrame(rows, columns=column_names)

        # Định dạng lại thời gian (nếu cần)
        data["Thời gian vào lớp"] = pd.to_datetime(data["Thời gian vào lớp"]).dt.strftime("%H:%M:%S")

        # Ghi dữ liệu vào file CSV
        data.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"Dữ liệu đã được ghi vào file {output_file}")
    except sqlite3.Error as e:
        print(f"Lỗi khi truy vấn dữ liệu: {e}")
    finally:
        conn.close()

# Gọi hàm ghi file sau khi kết thúc vòng lặp
write_to_csv()



# Giải phóng tài nguyên
cam.release()
cv2.destroyAllWindows()
del known_face_encodings
