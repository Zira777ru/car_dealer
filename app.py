from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cars.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    trim = db.Column(db.String(100))  # Комплектация
    vin = db.Column(db.String(17), unique=True)  # VIN
    driveline = db.Column(db.String(50))  # Привод
    carfax_report = db.Column(db.String(200))  # Ссылка на отчет Carfax
    mileage = db.Column(db.Integer)  # Пробег
    fuel_type = db.Column(db.String(50))  # Тип топлива
    owners = db.Column(db.Integer)  # Количество владельцев
    engine = db.Column(db.String(100))  # Двигатель
    price = db.Column(db.Float)  # Цена
    body_style = db.Column(db.String(50))  # Тип кузова
    photos = relationship('Photo', backref='car', lazy=True)

    def __repr__(self):
        return f"Car('{self.brand}', '{self.model}', {self.year}, '{self.vin}')"


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    path = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"Photo('{self.path}')"

with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_car', methods=['GET', 'POST'])
def add_car():
    if request.method == 'POST':
        # Получаем данные из формы
        brand = request.form['brand']
        model = request.form['model']
        year = request.form['year']
        trim = request.form.get('trim')
        vin = request.form.get('vin')
        driveline = request.form.get('driveline')
        carfax_report = request.form.get('carfax_report')
        mileage = request.form.get('mileage')
        fuel_type = request.form.get('fuel_type')
        owners = request.form.get('owners')
        engine = request.form.get('engine')
        price = request.form.get('price')
        body_style = request.form.get('body_style')
        
        # Создаем новый экземпляр автомобиля
        new_car = Car(
            brand=brand, model=model, year=year, trim=trim, vin=vin,
            driveline=driveline, carfax_report=carfax_report, mileage=mileage,
            fuel_type=fuel_type, owners=owners, engine=engine, price=price,
            body_style=body_style
        )
        db.session.add(new_car)
        db.session.commit()

        # Обработка загрузки фотографий
        photos = request.files.getlist('photos')
        for photo in photos:
            if photo and photo.filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS:
                # Создаем папку для сохранения файлов, если она не существует
                folder_path = os.path.join(UPLOAD_FOLDER, str(request.form.get("vin")))
                os.makedirs(folder_path, exist_ok=True)
                filename = secure_filename(photo.filename)
                # filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                filepath = os.path.join(f'{UPLOAD_FOLDER}/{request.form.get("vin")}', filename)
                photo.save(filepath)
                # Сохраняем относительный путь в базу данных
                new_photo = Photo(car_id=new_car.id, path='/'+filepath)
                db.session.add(new_photo)
                db.session.commit()

        return redirect(url_for('index'))
    else:
        return render_template('add_car.html')



@app.route('/')
def index():
    cars = Car.query.all()
    return render_template('index.html', cars=cars)

@app.route('/admin')
def admin():
    cars = Car.query.all()
    return render_template('admin.html', cars=cars)

@app.route('/car/<int:car_id>', methods=['GET', 'POST'])
def car_detail(car_id):
    car = Car.query.get_or_404(car_id)
    
    if request.method == 'POST':
        loan_amount = float(request.form['loan_amount'])
        interest_rate = float(request.form['interest_rate']) / 100
        loan_term = int(request.form['loan_term'])
        
        monthly_interest_rate = interest_rate / 12
        num_payments = loan_term * 12
        
        monthly_payment = (loan_amount * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** -num_payments)
        
        return render_template('car_detail.html', car=car, monthly_payment=monthly_payment, enumerate=enumerate)
    
    return render_template('car_detail.html', car=car, enumerate=enumerate)

@app.route('/photo/delete/<int:photo_id>', methods=['POST'])
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)  # Находим фотографию в базе данных

    # Удаляем запись о фотографии из базы данных
    db.session.delete(photo)
    db.session.commit()

    # Удаляем файл фотографии с сервера (если это необходимо)
    # Добавьте здесь соответствующий код для удаления файла

    # Перенаправляем пользователя на страницу редактирования автомобиля
    return redirect(url_for('edit_car', car_id=photo.car_id))

@app.route('/car/edit/<int:car_id>', methods=['GET', 'POST'])
def edit_car(car_id):
    car = Car.query.get_or_404(car_id)
    if request.method == 'POST':
        # Обработка данных формы редактирования
        car.brand = request.form['brand']
        car.model = request.form['model']
        car.year = request.form['year']
        car.trim = request.form.get('trim')
        car.vin = request.form.get('vin')
        car.driveline = request.form.get('driveline')
        car.carfax_report = request.form.get('carfax_report')
        car.mileage = request.form.get('mileage')
        car.fuel_type = request.form.get('fuel_type')
        car.owners = request.form.get('owners')
        car.engine = request.form.get('engine')
        car.price = request.form.get('price')
        car.body_style = request.form.get('body_style')
        if 'photos[]' in request.files:
            photos = request.files.getlist('photos[]')
            for photo in photos:
                if photo.filename != '' and allowed_file(photo.filename):
                    filename = secure_filename(photo.filename)
                    filepath = os.path.join(f'{UPLOAD_FOLDER}/{request.form.get("vin")}', filename)
                    photo.save(filepath)
                    new_photo = Photo(path=filepath, car_id=car.id)
                    db.session.add(new_photo)
        db.session.commit()
        return redirect(url_for('car_detail', car_id=car.id))
    return render_template('edit_car.html', car=car)


@app.route('/car/delete/<int:car_id>', methods=['GET', 'POST'])
def delete_car(car_id):
    car = Car.query.get_or_404(car_id)
    
    # Удаляем все фотографии, связанные с удаляемым автомобилем
    for photo in car.photos:
        db.session.delete(photo)
    
    # Удаляем сам автомобиль
    db.session.delete(car)
    db.session.commit()
    
    # flash('Car deleted successfully', 'success')
    return redirect(url_for('index'))



# if __name__ == '__main__':
#     app.run(debug=True)
