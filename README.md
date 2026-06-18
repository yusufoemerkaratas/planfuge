# Plan2Print - Proje Planlama ve İş Takip Sistemi

Plan2Print, inşaat, yazılım geliştirme, eğitim ve diğer birçok sektörde proje yönetimi ve görev takibi için tasarlanmış kapsamlı bir web uygulamasıdır. Kullanıcıların proje oluşturmasına, görevler atamasına, ilerlemeyi izlemesine ve raporlar almasına olanak tanır.

![Logo](docs/images/plan2print_logo.png)

## 🚀 Özellikler

- **Proje Yönetimi:** Proje oluşturma, düzenleme, silme ve durum yönetimi
- **Görev Yönetimi:** Görev atama, önceliklendirme, son tarihler ve durum takibi
- **Kullanıcı Rolleri:** Yönetici, proje yöneticisi, ekip üyesi ve misafir rolleri
- **İlerleme Takibi:** Yüzde hesaplamalı ilerleme göstergeleri ve görsel grafikler
- **Raporlama:** Detaylı proje raporları ve filtreleme seçenekleri
- **Güvenli Kimlik Doğrulama:** E-posta/parola ve sosyal medya ile giriş
- **Kullanıcı Dostu Arayüz:** Modern, responsive tasarım

---

## 📋 Kurulum

### Ön Gereksinimler

- **Node.js** 16.x veya daha yenisi
- **npm** 8.x veya daha yenisi
- **PostgreSQL** 12.x veya daha yenisi

### Adım 1: Depoyu Klonlama

```bash
git clone https://github.com/beyzabetulay/planfuge.git
cd planfuge
```

### Adım 2: Bağımlılıkları Kurma

```bash
npm install
```

### Adım 3: PostgreSQL Veritabanı Kurulumu

1. PostgreSQL sunucusunu başlatın
2. Yeni bir veritabanı oluşturun:

```sql
CREATE DATABASE plan2print;
```

3. Veritabanı kullanıcısını oluşturun (opsiyonel):

```sql
CREATE USER plan2print_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE plan2print TO plan2print_user;
```

### Adım 4: Ortam Değişkenlerini Yapılandırma

`src/config/.env` dosyasını kopyalayın ve düzenleyin:

```bash
cp src/config/.env .env
```

`.env` dosyasını aşağıdaki gibi düzenleyin:

```env
# Application Settings
PORT=3000
NODE_ENV=development

# Database Settings
DB_TYPE=postgres
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=plan2print
DB_USER=plan2print_user
DB_PASSWORD=your_password
```

### Adım 5: Veritabanı Migrationları

Migrationları çalıştırın:

```bash
npx prisma migrate dev --name init
```

### Adım 6: Başlatma

Uygulamayı başlatın:

```bash
npm run start
```

Uygulama `http://localhost:3000` adresinde çalışacaktır.

---

## 👥 Kullanıcı Rolleri

### Yönetici (Admin)

- Tüm projeleri görüntüleyebilir
- Tüm kullanıcıları yönetebilir
- Sistem ayarlarını yapabilir

### Proje Yöneticisi (Project Manager)

- Kendi oluşturduğu projeleri yönetebilir
- Proje görevlerini atayabilir
- İlerleme takibi yapabilir

### Ekip Üyesi (Team Member)

- Kendisine atanan görevleri görüntüleyebilir
- Görev durumunu güncelleyebilir
- İlerleme katkısı yapabilir

### Misafir (Guest)

- Proje özetlerini görüntüleyebilir
- Genel bilgilere erişebilir

---

## 📊 Mimari

```
Plan2Print (Frontend)
│
├── src/
│   ├── api/          # API istekleri
│   ├── components/   # React bileşenleri
│   │   ├── projects/  # Proje bileşenleri
│   │   ├── tasks/     # Görev bileşenleri
│   │   ├── auth/      # Kimlik doğrulama bileşenleri
│   │   └── shared/    # Paylaşılan bileşenler
│   ├── config/       # Konfigürasyon
│   ├── hooks/        # React hook'ları
│   ├── layouts/      # Layout bileşenleri
│   ├── pages/        # Sayfa bileşenleri
│   ├── services/     # Servisler
│   ├── store/        # Redux store
│   └── utils/        # Yardımcı fonksiyonlar
│
├── public/           # Statik dosyalar
├── server/           # Backend
│   ├── config/       # Backend konfigürasyonu
│   ├── controllers/  # Controller katmanı
│   ├── middlewares/  # Middleware'ler
│   ├── routes/       # Rota tanımları
│   ├── services/     # İş mantığı
│   ├── models/       # Prisma modeller
│   └── utils/        # Yardımcı fonksiyonlar
│
└── prisma/           # Prisma şemaları
```

---

## 🛠️ Teknolojiler

### Frontend

- **React** - UI kütüphanesi
- **TypeScript** - Tip güvenliği
- **Redux Toolkit** - State yönetimi
- **Material-UI** - UI bileşenleri
- **Axios** - API istekleri
- **React Router** - Navigasyon
- **Formik + Yup** - Form yönetimi
- **Chart.js** - Grafikler
- **React Datepicker** - Tarih seçimi

### Backend

- **Express** - Web framework
- **TypeScript** - Tip güvenliği
- **Prisma** - ORM
- **PostgreSQL** - Veritabanı
- **Bcrypt** - Şifre hashleme
- **JWT** - Kimlik doğrulama
- **Helmet** - Güvenlik
- **Winston** - Loglama

### Geliştirme Araçları

- **Vite** - Frontend build aracı
- **ESLint** - Kod kalitesi
- **Prettier** - Formatlama
- **Docker** - Konteynerleştirme (opsiyonel)

---

## 🔌 API Endpoint'ler

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Yeni kullanıcı kaydı |
| POST | `/api/auth/login` | Giriş yap |
| POST | `/api/auth/logout` | Çıkış yap |
| GET | `/api/auth/me` | Mevcut kullanıcı bilgilerini getir |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | Tüm kullanıcıları getir |
| GET | `/api/users/:id` | Kullanıcı bilgilerini getir |
| PUT | `/api/users/:id` | Kullanıcı bilgilerini güncelle |
| DELETE | `/api/users/:id` | Kullanıcıyı sil |

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects` | Tüm projeleri getir |
| GET | `/api/projects/:id` | Proje bilgilerini getir |
| POST | `/api/projects` | Proje oluştur |
| PUT | `/api/projects/:id` | Proje bilgilerini güncelle |
| DELETE | `/api/projects/:id` | Proje sil |
| GET | `/api/projects/:id/progress` | Proje ilerleme raporu |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | Tüm görevleri getir |
| GET | `/api/tasks/:id` | Görev bilgilerini getir |
| POST | `/api/tasks` | Görev oluştur |
| PUT | `/api/tasks/:id` | Görev bilgilerini güncelle |
| DELETE | `/api/tasks/:id`