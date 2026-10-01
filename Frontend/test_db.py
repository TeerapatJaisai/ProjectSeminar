import mysql.connector
import os

try:
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    print("เชื่อมต่อฐานข้อมูลสำเร็จ!")

    cursor = db.cursor()
    cursor.execute("SELECT * FROM foods")
    rows = cursor.fetchall()

    print("ข้อมูลใน foods:")
    for row in rows:
        print(row)

    cursor.close()
    db.close()

except Exception as e:
    print("เชื่อมต่อไม่สำเร็จ:")
    print(e)