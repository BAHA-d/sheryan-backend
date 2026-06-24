FROM python:3.12-slim

# 2️⃣ منع بايثون من كتابة ملفات .pyc على القرص داخل الحاوية
ENV PYTHONDONTWRITEBYTECODE=1
# 3️⃣ منع بايثون من تخزين مخرجات الـ Terminal مؤقتاً لكي تظهر الـ Logs فوراً
ENV PYTHONUNBUFFERED=1

# 4️⃣ تحديد مجلد العمل الافتراضي داخل الحاوية
WORKDIR /app

# 5️⃣ تثبيت التبعيات التي قد تحتاجها بعض مكتبات بايثون للـ Compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 6️⃣ نسخ ملف الحزم أولاً للاستفادة من الـ Caching في دوكر
COPY requirements.txt /app/

# 7️⃣ تثبيت حزم بايثون داخل الحاوية
RUN pip install --no-cache-dir -r requirements.txt

# 8️⃣ نسخ بقية ملفات المشروع بالكامل إلى الحاوية
COPY . /app/

# 9️⃣ الأمر الافتراضي لتشغيل السيرفر داخل الحاوية
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]