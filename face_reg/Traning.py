import os
import sqlite3
import face_recognition

# Đường dẫn đến thư mục chứa dữ liệu khuôn mặt
path = 'dataSet'

# Hàm khởi tạo cơ sở dữ liệu SQLite
def initialize_database():
    conn = sqlite3.connect("FaceBase.db")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS FaceEncodings (
            ID INTEGER PRIMARY KEY,
            Encoding BLOB
        )
    ''')
    conn.commit()
    conn.close()

# Hàm lưu mã nhận diện khuôn mặt vào SQLite
def save_encoding_to_db(id, encoding):
    conn = sqlite3.connect("FaceBase.db")
    try:
        # Lưu mã nhận diện vào cơ sở dữ liệu
        conn.execute("INSERT OR REPLACE INTO FaceEncodings (ID, Encoding) VALUES (?, ?)", 
                     (id, encoding.tobytes()))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

# Hàm đọc ảnh từ thư mục và trích xuất khuôn mặt
def get_face_encodings_and_ids(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(('png', 'jpg', 'jpeg'))]
    encodings = []
    ids = []

    for imagePath in imagePaths:
        # Đọc ID từ tên file
        id = int(os.path.split(imagePath)[-1].split('.')[1])
        print(f"Processing ID: {id}, File: {imagePath}")

        # Đọc ảnh và chuyển sang RGB
        image = face_recognition.load_image_file(imagePath)

        # Tìm khuôn mặt và trích xuất mã nhận diện
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            encoding = face_encodings[0]  # Giả sử mỗi ảnh chỉ có một khuôn mặt
            encodings.append(encoding)
            ids.append(id)
            
            # Lưu vào cơ sở dữ liệu
            save_encoding_to_db(id, encoding)
        else:
            print(f"No face found in {imagePath}")

    return ids, encodings

# Khởi tạo cơ sở dữ liệu
initialize_database()

# Đọc và xử lý khuôn mặt
ids, encodings = get_face_encodings_and_ids(path)

print("Face encodings and IDs have been saved to the database.")

