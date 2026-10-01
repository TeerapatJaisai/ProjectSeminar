from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

import mysql.connector
from mysql.connector import Error

import requests

import os
import base64
import time
import json
import threading

from datetime import date


app = Flask(__name__)


# ==================================================
# 50 วัตถุดิบ
# ==================================================

INGREDIENTS = [
    "หมู",
    "ไก่",
    "เนื้อวัว",
    "ปลา",
    "กุ้ง",
    "ปลาหมึก",
    "ปู",
    "ปลาแซลมอน",
    "ไส้กรอก",
    "แฮม",
    "เบคอน",
    "ไข่",
    "เต้าหู้",
    "นม",
    "โยเกิร์ต",
    "ชีส",
    "เนย",
    "ข้าว",
    "เส้นก๋วยเตี๋ยว",
    "ขนมปัง",
    "แครอท",
    "มันฝรั่ง",
    "มะเขือเทศ",
    "แตงกวา",
    "กะหล่ำปลี",
    "ผักกาดขาว",
    "ผักกาดหอม",
    "ผักโขม",
    "ผักบุ้ง",
    "บรอกโคลี",
    "ดอกกะหล่ำ",
    "ข้าวโพด",
    "ฟักทอง",
    "เห็ด",
    "หอมหัวใหญ่",
    "กระเทียม",
    "ขิง",
    "พริก",
    "ต้นหอม",
    "ผักชี",
    "มะนาว",
    "เลมอน",
    "แอปเปิล",
    "กล้วย",
    "ส้ม",
    "แตงโม",
    "สับปะรด",
    "มะม่วง",
    "อะโวคาโด",
    "สตรอว์เบอร์รี"
]


# ==================================================
# DATABASE
# ==================================================

def get_db_connection():

    return mysql.connector.connect(
        host=os.getenv(
            "DB_HOST",
            "localhost"
        ),

        user=os.getenv(
            "DB_USER",
            "root"
        ),

        password=os.getenv(
            "DB_PASSWORD",
            ""
        ),

        database=os.getenv(
            "DB_NAME",
            "smart_fridge"
        ),

        charset="utf8mb4"
    )


# ==================================================
# GEMINI
# ==================================================

API_KEY = os.environ.get(
    "GEMINI_API_KEY"
)


if API_KEY:

    client = genai.Client(
        api_key=API_KEY,

        http_options=types.HttpOptions(
            timeout=30000
        )
    )

    print(
        "Gemini API: OK"
    )

else:

    client = None

    print(
        "WARNING: GEMINI_API_KEY is not set"
    )


# ใช้โมเดลที่มีอยู่ใน Gemini API ปัจจุบัน
MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.7-flash"
]


# ==================================================
# LINE
# ==================================================

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get(
    "LINE_CHANNEL_ACCESS_TOKEN"
)

LINE_USER_ID = os.environ.get(
    "LINE_USER_ID"
)


# ==================================================
# HOME
# ==================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# ==================================================
# GET FOODS
# ==================================================

@app.route(
    "/foods",
    methods=["GET"]
)
def get_foods():

    conn = None
    cursor = None

    try:

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT
                id,
                name,
                quantity,
                location,
                added_date,
                expiry_date
            FROM foods
            ORDER BY expiry_date ASC
        """)

        rows = cursor.fetchall()

        foods = []

        for row in rows:

            foods.append({

                "id":
                    row["id"],

                "name":
                    row["name"],

                "quantity":
                    row["quantity"],

                "location":
                    row["location"],

                "added_date":
                    str(
                        row["added_date"]
                    ),

                "expiry":
                    str(
                        row["expiry_date"]
                    )
            })


        return jsonify(
            foods
        )


    except Error as e:

        print(
            "MYSQL ERROR:"
        )

        print(e)


        return jsonify({

            "success": False,

            "message":
                str(e)

        }), 500


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


# ==================================================
# ADD FOOD
# ==================================================

@app.route(
    "/foods",
    methods=["POST"]
)
def add_food():

    data = (
        request.get_json()
        or {}
    )


    name = (
        data
        .get("name", "")
        .strip()
    )


    quantity = data.get(
        "quantity",
        "ไม่ระบุ"
    )


    location = data.get(
        "location",
        "ช่องธรรมดา"
    )


    expiry = (
        data
        .get("expiry", "")
        .strip()
    )


    if not name:

        return jsonify({

            "success": False,

            "message":
                "กรุณากรอกชื่ออาหาร"

        }), 400


    if not expiry:

        return jsonify({

            "success": False,

            "message":
                "กรุณากรอกวันหมดอายุ"

        }), 400


    conn = None
    cursor = None


    try:

        conn = get_db_connection()

        cursor = conn.cursor()


        today = date.today()


        cursor.execute("""

            INSERT INTO foods
            (
                name,
                quantity,
                location,
                added_date,
                expiry_date
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )

        """, (

            name,
            quantity,
            location,
            today,
            expiry

        ))


        conn.commit()


        new_food = {

            "id":
                cursor.lastrowid,

            "name":
                name,

            "quantity":
                quantity,

            "location":
                location,

            "added_date":
                str(today),

            "expiry":
                expiry

        }


        return jsonify({

            "success":
                True,

            "food":
                new_food

        })


    except Error as e:

        print(
            "MYSQL ERROR:"
        )

        print(e)


        return jsonify({

            "success": False,

            "message":
                str(e)

        }), 500


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


# ==================================================
# EDIT FOOD
# ==================================================

@app.route(
    "/foods/<int:food_id>",
    methods=["PUT"]
)
def edit_food(food_id):

    data = (
        request.get_json()
        or {}
    )


    conn = None
    cursor = None


    try:

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        cursor.execute("""

            SELECT *

            FROM foods

            WHERE id = %s

        """, (
            food_id,
        ))


        old_food = cursor.fetchone()


        if not old_food:

            return jsonify({

                "success": False,

                "message":
                    "ไม่พบอาหาร"

            }), 404


        name = data.get(
            "name",
            old_food["name"]
        )


        quantity = data.get(
            "quantity",
            old_food["quantity"]
        )


        location = data.get(
            "location",
            old_food["location"]
        )


        expiry = data.get(

            "expiry",

            str(
                old_food[
                    "expiry_date"
                ]
            )

        )


        cursor.execute("""

            UPDATE foods

            SET
                name = %s,
                quantity = %s,
                location = %s,
                expiry_date = %s

            WHERE id = %s

        """, (

            name,
            quantity,
            location,
            expiry,
            food_id

        ))


        conn.commit()


        updated_food = {

            "id":
                food_id,

            "name":
                name,

            "quantity":
                quantity,

            "location":
                location,

            "added_date":
                str(
                    old_food[
                        "added_date"
                    ]
                ),

            "expiry":
                str(expiry)

        }


        return jsonify({

            "success":
                True,

            "food":
                updated_food

        })


    except Error as e:

        print(
            "MYSQL ERROR:"
        )

        print(e)


        return jsonify({

            "success": False,

            "message":
                str(e)

        }), 500


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


# ==================================================
# DELETE FOOD
# ==================================================

@app.route(
    "/foods/<int:food_id>",
    methods=["DELETE"]
)
def delete_food(food_id):

    conn = None
    cursor = None


    try:

        conn = get_db_connection()

        cursor = conn.cursor()


        cursor.execute("""

            DELETE FROM foods

            WHERE id = %s

        """, (
            food_id,
        ))


        conn.commit()


        if cursor.rowcount == 0:

            return jsonify({

                "success": False,

                "message":
                    "ไม่พบอาหาร"

            }), 404


        return jsonify({

            "success":
                True

        })


    except Error as e:

        print(
            "MYSQL ERROR:"
        )

        print(e)


        return jsonify({

            "success": False,

            "message":
                str(e)

        }), 500


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


# ==================================================
# GEMINI JSON HELPER
# ==================================================

def generate_json_ai(
    prompt,
    schema,
    image_part=None
):

    if client is None:

        raise Exception(
            "ยังไม่ได้ตั้ง GEMINI_API_KEY"
        )


    last_error = None


    for model in MODELS:


        for attempt in range(2):

            try:

                print(
                    f"AI model: {model} "
                    f"attempt {attempt + 1}/2"
                )


                contents = [
                    prompt
                ]


                if image_part:

                    contents.append(
                        image_part
                    )


                response = (
                    client.models
                    .generate_content(

                        model=model,

                        contents=contents,

                        config=
                            types
                            .GenerateContentConfig(

                                response_mime_type=
                                    "application/json",

                                response_schema=
                                    schema,

                                max_output_tokens=
                                    2000
                            )
                    )
                )


                if (
                    response.parsed
                    is not None
                ):

                    if isinstance(
                        response.parsed,
                        dict
                    ):

                        return response.parsed


                text = (
                    response.text
                    or ""
                ).strip()


                if text:

                    try:

                        return json.loads(
                            text
                        )

                    except (
                        json.JSONDecodeError
                    ):

                        pass


                raise Exception(
                    "AI ส่ง JSON ว่าง"
                )


            except Exception as e:

                last_error = e

                error_text = str(e)


                print(
                    "AI ERROR:"
                )

                print(
                    error_text
                )


                # 503

                if (
                    "503"
                    in error_text

                    or

                    "UNAVAILABLE"
                    in error_text
                ):

                    if attempt == 0:

                        time.sleep(2)

                        continue

                    break


                # 429

                if "429" in error_text:

                    # ถ้าเป็น daily quota
                    # ไม่ยิงซ้ำหลายรอบ

                    if (
                        "quota"
                        in error_text.lower()

                        and

                        "PerDay"
                        in error_text
                    ):

                        raise Exception(
                            "โควตา Gemini วันนี้ครบแล้ว"
                        )


                    if attempt == 0:

                        time.sleep(3)

                        continue

                    break


                # timeout

                if (
                    "timeout"
                    in error_text.lower()

                    or

                    "timed out"
                    in error_text.lower()
                ):

                    if attempt == 0:

                        time.sleep(2)

                        continue

                    break


                break


    raise Exception(
        "AI วิเคราะห์ไม่สำเร็จ: "
        +
        str(last_error)
    )


# ==================================================
# AI FOOD SCAN
# ==================================================

def analyze_food_image(
    image_bytes,
    mime_type
):

    prompt = """

คุณคือ AI สำหรับระบบ Smart Fridge

วิเคราะห์ภาพอาหารและระบุวัตถุดิบหลักที่เห็น

กฎสำคัญ:

1. name ต้องเลือกจาก 50 รายการเท่านั้น
2. ห้ามสร้างชื่อใหม่
3. ถ้ามีหลายอย่างให้เลือกสิ่งที่เห็นชัดที่สุด
4. ให้ประมาณปริมาณ
5. ถ้าไม่แน่ใจให้เลือกสิ่งที่ใกล้เคียงที่สุด

"""


    image_part = (
        types.Part.from_bytes(

            data=image_bytes,

            mime_type=mime_type
        )
    )


    schema = {

        "type":
            "object",

        "properties": {

            "name": {

                "type":
                    "string",

                "enum":
                    INGREDIENTS
            },

            "quantity": {

                "type":
                    "string"
            },

            "confidence": {

                "type":
                    "string"
            }
        },

        "required": [

            "name",

            "quantity",

            "confidence"
        ]
    }


    return generate_json_ai(

        prompt,

        schema,

        image_part
    )


# ==================================================
# SCAN
# ==================================================

@app.route(
    "/scan",
    methods=["POST"]
)
def scan_food():

    try:

        print("")
        print(
            "=============================="
        )
        print(
            "START AI SCAN"
        )
        print(
            "=============================="
        )


        if client is None:

            return jsonify({

                "success":
                    False,

                "message":
                    "ยังไม่ได้ตั้ง GEMINI_API_KEY"

            }), 500


        data = (
            request.get_json()
            or {}
        )


        image_data = data.get(
            "image"
        )


        if not image_data:

            return jsonify({

                "success":
                    False,

                "message":
                    "ไม่พบรูปภาพ"

            }), 400


        if "," in image_data:

            header, image_base64 = (
                image_data.split(
                    ",",
                    1
                )
            )

        else:

            header = ""

            image_base64 = (
                image_data
            )


        if "image/png" in header:

            mime_type = (
                "image/png"
            )

        elif "image/webp" in header:

            mime_type = (
                "image/webp"
            )

        else:

            mime_type = (
                "image/jpeg"
            )


        try:

            image_bytes = (
                base64.b64decode(
                    image_base64
                )
            )

        except Exception:

            return jsonify({

                "success":
                    False,

                "message":
                    "รูปภาพไม่ถูกต้อง"

            }), 400


        if len(image_bytes) > (
            10 * 1024 * 1024
        ):

            return jsonify({

                "success":
                    False,

                "message":
                    "รูปใหญ่เกิน 10 MB"

            }), 400


        result = (
            analyze_food_image(

                image_bytes,

                mime_type
            )
        )


        if (
            result.get("name")
            not in INGREDIENTS
        ):

            return jsonify({

                "success":
                    False,

                "message":
                    "AI ส่งชื่อวัตถุดิบไม่ถูกต้อง"

            }), 500


        return jsonify({

            "success":
                True,

            "result": {

                "name":
                    result.get(
                        "name",
                        "ไม่ทราบ"
                    ),

                "quantity":
                    result.get(
                        "quantity",
                        "ไม่ระบุ"
                    ),

                "confidence":
                    result.get(
                        "confidence",
                        "-"
                    )
            }
        })


    except Exception as e:

        print(
            "FINAL AI ERROR:"
        )

        print(e)


        return jsonify({

            "success":
                False,

            "message":
                str(e)

        }), 500


# ==================================================
# GET FOOD DATA
# ==================================================

def get_food_data():

    conn = None
    cursor = None


    try:

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        cursor.execute("""

            SELECT
                id,
                name,
                quantity,
                location,
                added_date,
                expiry_date

            FROM foods

            ORDER BY expiry_date ASC

        """)


        return cursor.fetchall()


    except Error as e:

        raise Exception(
            "MySQL Error: "
            +
            str(e)
        )


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


# ==================================================
# AI MENU
# ==================================================

def analyze_menu_suggestions(
    rows
):

    today = date.today()

    foods_text = ""


    for food in rows:

        expiry_date = (
            food["expiry_date"]
        )


        days_left = (
            expiry_date
            -
            today
        ).days


        if days_left < 0:

            status = (
                "หมดอายุแล้ว"
            )

        elif days_left == 0:

            status = (
                "หมดอายุวันนี้"
            )

        elif days_left <= 3:

            status = (
                f"เหลือ {days_left} วัน "
                "(ใกล้หมดอายุ)"
            )

        else:

            status = (
                f"เหลือ {days_left} วัน"
            )


        foods_text += f"""

อาหาร: {food['name']}
ปริมาณ: {food['quantity']}
สถานที่: {food['location']}
วันหมดอายุ: {expiry_date}
สถานะ: {status}

"""


    prompt = f"""

คุณคือ AI ผู้ช่วยจัดเมนูของ Smart Fridge

วันนี้คือ {today}

อาหารในตู้เย็น:

{foods_text}

หน้าที่:

1. แนะนำ 5 เมนู
2. ใช้วัตถุดิบที่มีจริงให้มากที่สุด
3. ห้ามบอกว่าของที่ไม่มีเป็นของที่มี
4. แยกของที่มีและของที่ขาด
5. ถ้าต้องซื้อเพิ่มให้บอก
6. ให้ความสำคัญกับของใกล้หมดอายุ
7. บอกเหตุผล
8. บอกวิธีทำแบบง่าย
"""


    schema = {

        "type":
            "object",

        "properties": {

            "menus": {

                "type":
                    "array",

                "items": {

                    "type":
                        "object",

                    "properties": {

                        "menu_name": {

                            "type":
                                "string"
                        },

                        "available_ingredients": {

                            "type":
                                "array",

                            "items": {
                                "type":
                                    "string"
                            }
                        },

                        "missing_ingredients": {

                            "type":
                                "array",

                            "items": {
                                "type":
                                    "string"
                            }
                        },

                        "steps": {

                            "type":
                                "array",

                            "items": {
                                "type":
                                    "string"
                            }
                        },

                        "reason": {

                            "type":
                                "string"
                        },

                        "use_expiring_soon": {

                            "type":
                                "boolean"
                        }
                    },

                    "required": [

                        "menu_name",

                        "available_ingredients",

                        "missing_ingredients",

                        "steps",

                        "reason",

                        "use_expiring_soon"
                    ]
                }
            }
        },

        "required": [
            "menus"
        ]
    }


    return generate_json_ai(

        prompt,

        schema
    )


# ==================================================
# MENU SUGGESTIONS
# ==================================================

@app.route(
    "/menu-suggestions",
    methods=["GET"]
)
def menu_suggestions():

    try:

        if client is None:

            return jsonify({

                "success":
                    False,

                "message":
                    "ยังไม่ได้ตั้ง GEMINI_API_KEY"

            }), 500


        rows = get_food_data()


        if not rows:

            return jsonify({

                "success":
                    False,

                "message":
                    "ยังไม่มีอาหารในตู้เย็น"

            }), 400


        result = (
            analyze_menu_suggestions(
                rows
            )
        )


        return jsonify({

            "success":
                True,

            "menus":
                result.get(
                    "menus",
                    []
                )
        })


    except Exception as e:

        print(
            "MENU AI ERROR:"
        )

        print(e)


        return jsonify({

            "success":
                False,

            "message":
                str(e)

        }), 500


# ==================================================
# LINE - SAVE USER
# ==================================================

def save_line_user():

    if not LINE_USER_ID:

        return


    conn = None
    cursor = None


    try:

        conn = get_db_connection()

        cursor = conn.cursor()


        cursor.execute("""

            INSERT INTO users
            (line_user_id)

            VALUES (%s)

            ON DUPLICATE KEY UPDATE
            line_user_id =
                VALUES(line_user_id)

        """, (
            LINE_USER_ID,
        ))


        conn.commit()


        print(
            "LINE USER SAVED"
        )


    except Error as e:

        print(
            "LINE USER ERROR:"
        )

        print(e)


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


# ==================================================
# LINE - SEND MESSAGE
# ==================================================

def send_line_message(
    text,
    user_id=None
):

    token = (
        LINE_CHANNEL_ACCESS_TOKEN
    )


    target_user = (
        user_id
        or
        LINE_USER_ID
    )


    if not token:

        raise Exception(
            "ยังไม่ได้ตั้ง "
            "LINE_CHANNEL_ACCESS_TOKEN"
        )


    if not target_user:

        raise Exception(
            "ยังไม่ได้ตั้ง "
            "LINE_USER_ID"
        )


    url = (
        "https://api.line.me/"
        "v2/bot/message/push"
    )


    headers = {

        "Content-Type":
            "application/json",

        "Authorization":
            f"Bearer {token}"
    }


    payload = {

        "to":
            target_user,

        "messages": [

            {

                "type":
                    "text",

                "text":
                    text

            }

        ]
    }


    response = requests.post(

        url,

        headers=headers,

        json=payload,

        timeout=15
    )


    if response.status_code != 200:

        raise Exception(
            "LINE API Error: "
            +
            response.text
        )


    return True


# ==================================================
# TEST LINE
# ==================================================

@app.route(
    "/test-line",
    methods=["GET"]
)
def test_line():

    try:

        send_line_message(
            "✅ Smart Fridge\n\n"
            "ทดสอบระบบแจ้งเตือน LINE สำเร็จ"
        )


        return (
            "ส่ง LINE สำเร็จ"
        )


    except Exception as e:

        print(
            "TEST LINE ERROR:"
        )

        print(e)


        return (
            "ส่ง LINE ไม่สำเร็จ: "
            +
            str(e)
        ), 500


# ==================================================
# CREATE LINE TABLES
# ==================================================

def create_line_tables():

    conn = None
    cursor = None


    try:

        conn = get_db_connection()

        cursor = conn.cursor()


        cursor.execute("""

            CREATE TABLE IF NOT EXISTS users (

                id INT AUTO_INCREMENT PRIMARY KEY,

                line_user_id VARCHAR(100)
                NOT NULL UNIQUE

            )

        """)


        cursor.execute("""

            CREATE TABLE IF NOT EXISTS notifications (

                id INT AUTO_INCREMENT PRIMARY KEY,

                food_id INT NOT NULL,

                user_id INT NOT NULL,

                notification_date DATE NOT NULL,

                status VARCHAR(20)
                DEFAULT 'sent',

                UNIQUE KEY
                unique_notification
                (
                    food_id,
                    user_id,
                    notification_date
                ),

                FOREIGN KEY
                (food_id)
                REFERENCES foods(id)
                ON DELETE CASCADE,

                FOREIGN KEY
                (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE

            )

        """)


        conn.commit()


        print(
            "LINE TABLES: OK"
        )


    except Error as e:

        print(
            "LINE TABLE ERROR:"
        )

        print(e)


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


# ==================================================
# CHECK EXPIRY
# ==================================================

def check_expiry_notifications():

    if not LINE_CHANNEL_ACCESS_TOKEN:

        print(
            "LINE TOKEN NOT SET"
        )

        return


    conn = None
    cursor = None


    try:

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # ------------------------------------------
        # หาอาหารที่เหลือ 3 วัน / 1 วัน / วันนี้
        # ------------------------------------------

        cursor.execute("""

            SELECT

                id,

                name,

                quantity,

                location,

                expiry_date,

                DATEDIFF(
                    expiry_date,
                    CURDATE()
                ) AS days_left

            FROM foods

            WHERE DATEDIFF(
                expiry_date,
                CURDATE()
            ) IN (3, 1, 0)

            ORDER BY expiry_date ASC

        """)


        foods = (
            cursor.fetchall()
        )


        if not foods:

            print(
                "ไม่มีอาหารที่ต้องแจ้งเตือน"
            )

            return


        # ------------------------------------------
        # users
        # ------------------------------------------

        cursor.execute("""

            SELECT
                id,
                line_user_id

            FROM users

        """)


        users = (
            cursor.fetchall()
        )


        if not users:

            print(
                "ยังไม่มี LINE user"
            )

            return


        # ------------------------------------------
        # วนอาหาร
        # ------------------------------------------

        for food in foods:


            for user in users:

                # ----------------------------------
                # ป้องกันส่งซ้ำวันนี้
                # ----------------------------------

                cursor.execute("""

                    SELECT id

                    FROM notifications

                    WHERE food_id = %s

                    AND user_id = %s

                    AND notification_date =
                        CURDATE()

                """, (

                    food["id"],

                    user["id"]

                ))


                already_sent = (
                    cursor.fetchone()
                )


                if already_sent:

                    continue


                days_left = (
                    food["days_left"]
                )


                # ----------------------------------
                # ข้อความ
                # ----------------------------------

                if days_left == 3:

                    title = (
                        "⚠️ อาหารใกล้หมดอายุ"
                    )

                    time_text = (
                        "เหลืออีก 3 วัน"
                    )


                elif days_left == 1:

                    title = (
                        "🚨 อาหารใกล้หมดอายุ"
                    )

                    time_text = (
                        "เหลืออีก 1 วัน"
                    )


                else:

                    title = (
                        "🔴 อาหารหมดอายุวันนี้"
                    )

                    time_text = (
                        "หมดอายุวันนี้"
                    )


                message = f"""

{title}

🥬 อาหาร: {food["name"]}

📦 ปริมาณ: {food["quantity"]}

📍 ที่เก็บ: {food["location"]}

📅 วันหมดอายุ:
{food["expiry_date"]}

⏰ {time_text}

แนะนำให้นำวัตถุดิบนี้
ไปทำอาหารก่อนหมดอายุครับ

""".strip()


                # ----------------------------------
                # ส่ง LINE
                # ----------------------------------

                try:

                    send_line_message(

                        message,

                        user["line_user_id"]

                    )


                    # --------------------------------
                    # บันทึกว่าแจ้งแล้ว
                    # --------------------------------

                    cursor.execute("""

                        INSERT INTO notifications

                        (
                            food_id,
                            user_id,
                            notification_date,
                            status
                        )

                        VALUES
                        (
                            %s,
                            %s,
                            CURDATE(),
                            'sent'
                        )

                    """, (

                        food["id"],

                        user["id"]

                    ))


                    conn.commit()


                    print(
                        "LINE SENT:",
                        food["name"]
                    )


                except Exception as e:

                    print(
                        "LINE SEND ERROR:"
                    )

                    print(e)


    except Error as e:

        print(
            "EXPIRY MYSQL ERROR:"
        )

        print(e)


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


# ==================================================
# NOTIFICATION LOOP
# ==================================================

def notification_loop():

    print(
        "LINE notification system started"
    )


    while True:

        try:

            check_expiry_notifications()

        except Exception as e:

            print(
                "NOTIFICATION LOOP ERROR:"
            )

            print(e)


        # ตรวจทุก 1 ชั่วโมง

        time.sleep(
            60 * 60
        )


# ==================================================
# START NOTIFICATION SYSTEM
# ==================================================

def start_notification_system():

    create_line_tables()

    save_line_user()


    thread = threading.Thread(

        target=notification_loop,

        daemon=True

    )


    thread.start()


# ==================================================
# TEST DATABASE
# ==================================================

@app.route(
    "/test-db",
    methods=["GET"]
)
def test_db():

    conn = None
    cursor = None


    try:

        conn = get_db_connection()

        cursor = conn.cursor()


        cursor.execute(
            "SELECT COUNT(*) FROM foods"
        )


        count = (
            cursor.fetchone()[0]
        )


        return jsonify({

            "success":
                True,

            "message":
                "เชื่อมต่อ MySQL สำเร็จ",

            "food_count":
                count

        })


    except Error as e:

        return jsonify({

            "success":
                False,

            "message":
                str(e)

        }), 500


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":

    print("")
    print(
        "=============================="
    )
    print(
        "SMART FRIDGE"
    )
    print(
        "=============================="
    )


    if LINE_CHANNEL_ACCESS_TOKEN:

        print(
            "LINE: ON"
        )

    else:

        print(
            "LINE: OFF"
        )


    print(
        "Computer:"
        " https://127.0.0.1:5000"
    )


    print(
        "Phone:"
        " https://192.168.1.194:5000"
    )


    print(
        "=============================="
    )

    print("")


    # เริ่มระบบ LINE

    start_notification_system()


    app.run(

        host="0.0.0.0",

        port=5000,

        ssl_context="adhoc",

        debug=True,

        use_reloader=False

    )