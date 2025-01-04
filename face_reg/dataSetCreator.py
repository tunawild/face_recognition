import sqlite3
import os


def Taobang():
    # Kết nối tới cơ sở dữ liệu (nếu chưa có sẽ tạo mới)
    conn = sqlite3.connect('FaceBase.db')

    # Tạo con trỏ để thực hiện các câu lệnh SQL
    cursor = conn.cursor()

    # Tạo bảng nếu chưa tồn tại
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS People (
        ID INTEGER PRIMARY KEY NOT NULL,
        Name TEXT NOT NULL,
        LOP TEXT,
        ThờiGianVàoLớp TEXT,
        TrạngThái TEXT,
        VÀORA TEXT
    )
    ''')

    # Lưu thay đổi và đóng kết nối
    conn.commit()
    conn.close()


# Hàm chèn hoặc cập nhật dữ liệu vào SQLite
def insertOrUpdate(Id, Name, LOP):
    conn = sqlite3.connect("FaceBase.db")
    cursor = conn.cursor()
    
    # Kiểm tra xem ID đã tồn tại chưa
    cursor.execute("SELECT * FROM People WHERE ID=?", (Id,))
    isRecordExist = cursor.fetchone()
    
    if isRecordExist:
        cursor.execute("UPDATE People SET Name=? WHERE ID=?", (Name, Id))
    else:
        cursor.execute("INSERT INTO People(Id, Name, LOP) VALUES(?, ?, ?)", (Id, Name, LOP))
    
    conn.commit()
    conn.close()

# Kiểm tra thư mục dataSet
if not os.path.exists("dataSet"):
    os.makedirs("dataSet")

Taobang()

while True:
    # Nhập ID và tên người dùng
    id = input("Enter your ID: ")
    # Nhập ID = q để thoát  
    if id == 'q':
        break
    
    name = input("Enter your Name: ")
    LOP = input("Enter your lop: ")
    insertOrUpdate(id, name,LOP)



