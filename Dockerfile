# Menginstall base image
FROM python:3.9-buster

# Mengganti workdir
WORKDIR /app

# Melakukan copy file di folder ini menuju folder /app di container
COPY . /app

# Melakukan upgrade pip untuk memastikan semua requirements dapat terinstall
RUN python -m pip install --upgrade pip

# Menginstall semua requirement yang dibutuhkan
RUN pip install -r requirements.txt

# Membuka port 8000 agar dapat diakses dari luar container
EXPOSE 8000

# Menjalankan main.py
CMD [ "python", "main.py" ]


