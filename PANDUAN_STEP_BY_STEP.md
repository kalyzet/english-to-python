# 📋 PANDUAN STEP-BY-STEP - English to Python Translator

## 🎯 CARA MENGGUNAKAN PANDUAN INI

1. **Buka aplikasi:** `python main.py`
2. **Pilih salah satu alur** di bawah ini
3. **Copy-paste input** satu per satu ke aplikasi
4. **Klik "Translate"** setelah setiap input
5. **Klik "Run Code"** untuk test hasil

---

## 🚀 ALUR A: PEMULA (5 menit)

**Tujuan:** Belajar dasar-dasar translator

### Input 1: Assignment

```
set age to 25
```

**Hasil:** `age = 25`

### Input 2: Aritmatika

```
add 10 and 5
```

**Hasil:** `result = 10 + 5`

### Input 3: Conditional

```
if age greater than 18 then print adult
```

**Hasil:**

```python
if age > 18:
    print(adult)
```

### Input 4: Conditional dengan Else

```
if age greater than 30 then print old else print young
```

**Hasil:**

```python
if age > 30:
    print(old)
else:
    print(young)
```

---

## 🎓 ALUR B: SISTEM NILAI (10 menit)

**Tujuan:** Membuat sistem penilaian siswa

### Input 1: Setup Data

```
set student_name to Alice
```

### Input 2: Setup Nilai

```
set math_score to 85
```

### Input 3: Setup Nilai 2

```
set english_score to 92
```

### Input 4: Evaluasi Math

```
if math_score greater than 80 then print good_math else print poor_math
```

### Input 5: Evaluasi English

```
if english_score greater than 90 then print excellent_english else print good_english
```

### Input 6: Hitung Total

```
add math_score and english_score
```

### Input 7: Evaluasi Kelulusan

```
if result greater than 160 then print passed else print failed
```

**🎯 Hasil Akhir:** Sistem penilaian lengkap!

---

## 🌡️ ALUR C: MONITORING CUACA (8 menit)

**Tujuan:** Sistem monitoring cuaca otomatis

### Input 1: Setup Suhu

```
set temperature to 35
```

### Input 2: Setup Kelembaban

```
set humidity to 75
```

### Input 3: Cek Suhu

```
if temperature greater than 30 then print hot else print normal
```

### Input 4: Cek Kelembaban (Pattern WHEN-DO)

```
when humidity greater than 70 do print humid
```

### Input 5: Peringatan Ekstrem

```
if temperature greater than 40 then print danger else print safe
```

### Input 6: Multiple Condition

```
when temperature greater than 35 do print very_hot
```

**🎯 Hasil Akhir:** Sistem cuaca dengan berbagai kondisi!

---

## 🏪 ALUR D: KASIR TOKO (12 menit)

**Tujuan:** Sistem kasir dengan diskon dan pajak

### Input 1: Setup Harga

```
set item_price to 50000
```

### Input 2: Setup Quantity

```
set quantity to 3
```

### Input 3: Hitung Total

```
multiply item_price by quantity
```

### Input 4: Setup Total ke Variabel

```
set total to 150000
```

### Input 5: Setup Member Status

```
set is_member to true
```

### Input 6: Cek Member Discount

```
if is_member equals true then print member_discount else print no_discount
```

### Input 7: Cek Bulk Discount

```
if total greater than 100000 then print bulk_discount else print regular_price
```

### Input 8: Hitung Pajak

```
multiply total by 0.1
```

### Input 9: Final Check

```
if total greater than 200000 then print expensive else print affordable
```

**🎯 Hasil Akhir:** Sistem kasir lengkap dengan berbagai fitur!

---

## 🎮 ALUR E: GAME SCORING (15 menit)

**Tujuan:** Sistem scoring game dengan level dan lives

### Input 1-4: Setup Player

```
set player_name to Gamer123
set current_level to 5
set current_score to 2500
set lives_remaining to 3
```

### Input 5: Bonus Score

```
add current_score and 500
```

### Input 6: Update Score

```
set current_score to 3000
```

### Input 7: Check High Score

```
if current_score greater than 5000 then print high_score else print normal_score
```

### Input 8: Check Level Up

```
if current_level greater than 10 then print level_up else print continue_playing
```

### Input 9: Check Game Over

```
if lives_remaining equals 0 then print game_over else print still_alive
```

### Input 10: Bonus Life

```
when current_score greater than 2000 do print bonus_life
```

**🎯 Hasil Akhir:** Sistem game scoring lengkap!

---

## 📊 CHEAT SHEET - FORMAT YANG BENAR

### ✅ **Assignment:**

```
set [variable] to [value]
set age to 25
set name to John
```

### ✅ **Aritmatika:**

```
add [A] and [B]
subtract [A] from [B]
multiply [A] by [B]
divide [A] by [B]
```

### ✅ **Conditional:**

```
if [condition] then [action]
if [condition] then [action] else [other_action]
when [condition] do [action]
```

### ✅ **Operator:**

```
greater than → >
less than → <
equals → ==
```

---

## ⚠️ KESALAHAN UMUM

### ❌ **Yang Salah:**

-   `if age > 18` (tidak ada "then")
-   `when count = 0` (tidak ada "do")
-   `age = 25` (gunakan "set")
-   `10 + 5` (gunakan "add")

### ✅ **Yang Benar:**

-   `if age greater than 18 then print adult`
-   `when count equals 0 do print empty`
-   `set age to 25`
-   `add 10 and 5`

---

## 🎯 TIPS SUKSES

1. **Mulai dari Alur A** - Pelajari dasar dulu
2. **Satu input per waktu** - Jangan terburu-buru
3. **Perhatikan format** - Pastikan ada "then" dan "do"
4. **Test setiap step** - Klik "Run Code" untuk memastikan
5. **Ikuti urutan** - Jangan skip step

---

## 🎉 SELAMAT MENCOBA!

Pilih salah satu alur dan ikuti step-by-step. Semua fitur conditional statements sudah diperbaiki dan siap digunakan!

**Fitur Baru yang Sudah Diperbaiki:**

-   ✅ Print statements menghasilkan `print()` yang benar
-   ✅ Else clause fully implemented
-   ✅ Multiple conditional patterns (if-then, when-do)
-   ✅ Smart string vs variable detection
