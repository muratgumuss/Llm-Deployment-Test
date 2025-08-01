import sqlite3

"""
1. import sqlite3
Bu satır, Python'un standart kütüphanesindeki SQLite veritabanı modülünü içeri aktarır.

sqlite3, dosya tabanlı (embedded) bir veritabanı sistemidir.

Ekstra kurulum gerekmez, Python ile birlikte gelir.

Bu modül sayesinde veritabanı dosyası oluşturabilir, tablo açabilir, kayıt ekleyebilir ve sorgu yapabilirsin.
"""

# connect to sqlite 
connection = sqlite3.connect("student.db")

"""
2. sqlite3.connect("student.db")
student.db adında bir veritabanı dosyasına bağlantı açar.

Eğer dosya yoksa, otomatik olarak oluşturulur.

connection nesnesi üzerinden:

    tablo yaratabilir,

    veri ekleyebilir,

    sorgular çalıştırabilirsin.

Bu nesne, dosyaya erişim ve işlem için bir veritabanı oturumu (session) başlatır.
"""

# create a cursor object to insert record, create table
cursor = connection.cursor()

"""
3. connection.cursor()
cursor, veritabanı işlemlerini gerçekleştiren bir nesnedir.

SQL komutlarını (CREATE, INSERT, SELECT, UPDATE, DELETE gibi) çalıştırmak için kullanılır.

Veritabanı ile etkileşimde bu ara yüz üzerinden çalışılır.
"""

# create the table

table_info = """
create table STUDENT(NAME VARCHAR(25), CLASS VARCHAR(25),
SECTION VARCHAR(25), MARKS INT)
"""

"""
4. SQL tablo oluşturma sorgusu
    STUDENT adında bir tablo oluşturacak bir SQL komutudur.

    Sütunlar şunlardır:

        NAME: Öğrenci adı (25 karaktere kadar yazı)

        CLASS: Öğrencinin okuduğu alan veya sınıf

        SECTION: Hangi şube/şube kodu (örneğin A, B vs.)

        MARKS: Alınan not (tamsayı)

Eğer bu tablo daha önce oluşturulmuşsa, bu kod OperationalError verebilir: "table STUDENT already exists".
"""

cursor.execute(table_info)

"""
✅ 5. cursor.execute(table_info)
Yukarıda yazdığımız SQL komutunu çalıştırır.

Yani veritabanında STUDENT adında bir tablo oluşturur.
"""

# Insert some records

cursor.execute('''Insert Into STUDENT values('Murat','Data Science','A',90) ''')
cursor.execute('''Insert Into STUDENT values('Puji','Property Advisor','A',100) ''')

"""
➕ 6. Veri ekleme
STUDENT tablosuna iki öğrenci kaydı ekler.
Henüz veritabanına kalıcı olarak yazılmaz, commit() çağrısı gerekir.
"""
# Display all records
print("The inserted records are")
data = cursor.execute('''Select * from STUDENT''')

"""
7. Kayıtları görüntüleme
SELECT * FROM STUDENT: Tablodaki tüm kayıtları alır.

data, bir iterator’dır; her satır için bir tuple döner.

print(...) ile kullanıcıya gösterilir.
"""

for row in data:
    print (row)

"""
8. Kayıtların satır satır yazdırılması
Veritabanından gelen her bir row tuple'ını yazdırır.
"""

# Commit your changes in the database
connection.commit()

"""
9. Değişiklikleri kaydetme
Veritabanına yapılan değişiklikleri kalıcı olarak yazmak için kullanılır.

Eğer çağrılmazsa, INSERT işlemleri dosyaya yazılmaz, program kapanınca veri kaybolur.
"""

connection.close()

"""
10. Veritabanı bağlantısını kapatma
Veritabanı dosyasıyla olan bağlantıyı düzgünce kapatır.

Kaynakları serbest bırakır, dosya kilitlenmez.

En son adımda yapılmalıdır.
"""