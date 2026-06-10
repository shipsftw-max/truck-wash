from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('truck_wash.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>مغسلة الشاحنات</title>
        <style>
            body { font-family: Arial; padding: 20px; background: #f0f0f0; }
            .container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; }
            input, button { width: 100%; padding: 10px; margin: 10px 0; font-size: 16px; }
            button { background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .truck-card { background: #e9ecef; padding: 15px; border-radius: 10px; margin: 15px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚛 مغسلة الشاحنات</h1>
            <h3>🔍 مسح الباركود</h3>
            <input type="text" id="barcode" placeholder="ادخل الباركود">
            <button onclick="searchTruck()">بحث</button>
            <div id="result"></div>
            <hr>
            <a href="/register">➕ تسجيل شاحنة جديدة</a>
        </div>
        <script>
            async function searchTruck() {
                let barcode = document.getElementById('barcode').value;
                let res = await fetch('/get_truck?barcode=' + barcode);
                let data = await res.json();
                let div = document.getElementById('result');
                if (data.success) {
                    div.innerHTML = `<div class="truck-card">
                        <h4>🚛 ${data.truck.driver_name}</h4>
                        <p>اللوحة: ${data.truck.plate_number}</p>
                        <p>زيارات: ${data.truck.total_visits}</p>
                        <p>إجمالي: ${data.truck.total_spent} ريال</p>
                    </div>`;
                } else {
                    div.innerHTML = '<p style="color:red">❌ شاحنة غير مسجلة</p>';
                }
            }
        </script>
    </body>
    </html>
    '''

@app.route('/get_truck')
def get_truck():
    barcode = request.args.get('barcode')
    conn = get_db()
    truck = conn.execute('SELECT * FROM trucks WHERE barcode = ?', (barcode,)).fetchone()
    conn.close()
    if truck:
        return jsonify({'success': True, 'truck': dict(truck)})
    return jsonify({'success': False})

@app.route('/register')
def register():
    return '''
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>تسجيل شاحنة</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            .container { max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 10px; }
            input, button { width: 100%; padding: 10px; margin: 5px 0; }
            button { background: green; color: white; border: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>➕ تسجيل شاحنة جديدة</h1>
            <form action="/register_submit" method="POST">
                <input type="text" name="plate_number" placeholder="رقم اللوحة" required>
                <input type="text" name="driver_name" placeholder="اسم السائق" required>
                <input type="tel" name="phone" placeholder="رقم الجوال">
                <button type="submit">تسجيل</button>
            </form>
            <a href="/">← العودة</a>
        </div>
    </body>
    </html>
    '''

@app.route('/register_submit', methods=['POST'])
def register_submit():
    plate = request.form['plate_number']
    driver = request.form['driver_name']
    phone = request.form.get('phone', '')
    
    conn = get_db()
    barcode = f"TW{plate.replace(' ', '')}"
    try:
        conn.execute('INSERT INTO trucks (plate_number, driver_name, phone, barcode) VALUES (?, ?, ?, ?)',
                     (plate, driver, phone, barcode))
        conn.commit()
        conn.close()
        return f'''
        <html dir="rtl">
        <body style="text-align:center; padding:50px;">
            <h2>✅ تم التسجيل!</h2>
            <p><strong>الباركود:</strong> {barcode}</p>
            <a href="/">← امسح الباركود</a>
        </body>
        </html>
        '''
    except:
        conn.close()
        return '<p style="color:red">❌ رقم اللوحة موجود</p> <a href="/register">حاول مرة أخرى</a>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
