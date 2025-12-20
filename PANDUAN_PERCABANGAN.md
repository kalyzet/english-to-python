# 🔀 PANDUAN PERCABANGAN - English to Python Translator

## ✅ FORMAT YANG BENAR

### 1. **IF dengan THEN**

```
if [variabel] [operator] [nilai] then [aksi]
```

**Contoh:**

-   `if age greater than 18 then print adult`
-   `if score less than 60 then print fail`
-   `if count equals 0 then print empty`

**Output Python:**

```python
if age > 18:
    print(adult)
```

### 2. **WHEN dengan DO**

```
when [variabel] [operator] [nilai] do [aksi]
```

**Contoh:**

-   `when temperature greater than 30 do print hot`
-   `when status equals active do print running`

**Output Python:**

```python
if temperature > 30:
    print(hot)
```

### 3. **IF dengan ELSE** ✨ **BARU!**

```
if [variabel] [operator] [nilai] then [aksi1] else [aksi2]
```

**Contoh:**

-   `if age greater than 18 then print adult else print minor`
-   `if score less than 60 then print fail else print pass`

**Output Python:**

```python
if age > 18:
    print(adult)
else:
    print(minor)
```

## 🔧 OPERATOR YANG DIDUKUNG

| English        | Python | Contoh                   |
| -------------- | ------ | ------------------------ |
| `greater than` | `>`    | `if age greater than 18` |
| `less than`    | `<`    | `if score less than 60`  |
| `equals`       | `==`   | `if count equals 0`      |

## 🎯 CARA PENGGUNAAN DI APLIKASI

### **Step 1: Setup Variabel**

```
set age to 20
set score to 85
set temperature to 35
```

### **Step 2: Buat Percabangan**

```
if age greater than 18 then print adult
if score greater than 80 then print excellent else print good
when temperature greater than 30 do print hot
```

### **Step 3: Translate & Run**

1. Masukkan instruksi di Input Area
2. Klik **"Translate"**
3. Lihat kode Python di Output Area
4. Klik **"Run Code"** untuk menjalankan

## ⚠️ PENTING!

### ✅ **YANG BENAR:**

-   `if age greater than 18 then print adult` ← **ADA "then"**
-   `when count equals 0 do print empty` ← **ADA "do"**
-   `if score less than 60 then print fail else print pass` ← **ELSE CLAUSE**

### ❌ **YANG SALAH:**

-   `if age greater than 18` ← **TIDAK ADA "then"**
-   `when count equals 0` ← **TIDAK ADA "do"**

## 🚀 CONTOH LENGKAP

### **Input Sequence:**

```
1. set age to 20
2. set score to 85
3. if age greater than 18 then print adult
4. if score greater than 80 then print excellent else print good
```

### **Output Python:**

```python
age = 20
score = 85
if age > 18:
    print(adult)
if score > 80:
    print(excellent)
else:
    print(good)
```

## 🎉 FITUR BARU!

### ✨ **PRINT STATEMENTS YANG BENAR**

-   Sekarang `print adult` menghasilkan `print(adult)` bukan `pass`
-   Deteksi otomatis antara variabel dan string literal
-   `print pass` → `print("pass")` (string literal)
-   `print status` → `print(status)` (variabel)

### ✨ **ELSE CLAUSE SUPPORT**

-   IF-THEN-ELSE sekarang fully implemented
-   Mendukung aksi berbeda untuk kondisi true/false
-   Syntax error sudah diperbaiki

### ✨ **MULTIPLE CONDITIONAL PATTERNS**

-   `if...then` (original)
-   `when...do` (alternative)
-   `when...then` (alternative)
-   Semua pattern menghasilkan kode Python yang sama

## 📝 CATATAN

-   ✅ Print statements sekarang menghasilkan kode Python yang benar
-   ✅ Else clause sudah fully implemented
-   ✅ Deteksi otomatis variabel vs string literal
-   ✅ Multiple conditional patterns didukung
-   ⚠️ Variabel harus di-set terlebih dahulu sebelum digunakan dalam IF

## 🎉 SELAMAT MENCOBA!

Gunakan format di atas untuk membuat percabangan yang benar di English to Python Translator!
