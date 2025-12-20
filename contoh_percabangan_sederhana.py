#!/usr/bin/env python3
"""
Contoh Percabangan Sederhana - English to Python Translator
Contoh input yang benar-benar bisa digunakan
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from services.translation_engine import TranslationEngine

def main():
    engine = TranslationEngine()
    
    print("🎯 === CONTOH PERCABANGAN YANG BISA DIGUNAKAN ===\n")
    
    # Contoh yang realistis dan bisa dijalankan
    contoh = [
        # 1. Setup variabel dulu
        ("Setup Variabel", [
            "set age to 20",
            "set score to 85", 
            "set temperature to 35",
            "set status to active"
        ]),
        
        # 2. Percabangan sederhana
        ("Percabangan Sederhana", [
            "if age greater than 18",
            "if score greater than 80", 
            "if temperature greater than 30",
            "if status equals active"
        ]),
        
        # 3. Percabangan dengan kondisi berbeda
        ("Variasi Kondisi", [
            "if age less than 25",
            "if score equals 100",
            "when temperature greater than 40",
            "when status equals inactive"
        ])
    ]
    
    for kategori, instruksi_list in contoh:
        print(f"📂 {kategori}:")
        print("-" * 40)
        
        for instruksi in instruksi_list:
            result = engine.translate(instruksi)
            
            if result.success:
                print(f"✅ {instruksi}")
                print(f"   → {result.python_code}")
            else:
                print(f"❌ {instruksi}")
                print(f"   → ERROR: {result.error_message}")
            print()
        
        print()

def panduan_penggunaan():
    print("📖 === PANDUAN PENGGUNAAN PERCABANGAN ===\n")
    
    panduan = """
🔹 POLA YANG DIDUKUNG:

1. IF sederhana:
   • if [variabel] greater than [nilai]
   • if [variabel] less than [nilai]  
   • if [variabel] equals [nilai]

2. WHEN (sama dengan IF):
   • when [variabel] greater than [nilai]
   • when [variabel] equals [nilai]

3. Operator yang didukung:
   • greater than  →  >
   • less than     →  <
   • equals        →  ==

🔹 CARA PAKAI DI APLIKASI:

1. Buka aplikasi: python main.py
2. Masukkan setup variabel dulu:
   set age to 20
   
3. Kemudian buat percabangan:
   if age greater than 18
   
4. Klik "Translate" untuk lihat kode Python
5. Klik "Run Code" untuk menjalankan

🔹 CONTOH LENGKAP:

Input 1: set age to 20
Output:  age = 20

Input 2: if age greater than 18  
Output:  if age > 18:
             pass

🔹 CATATAN:
- Saat ini "else" clause dan "print" statements belum fully supported
- Fokus pada kondisi IF sederhana dulu
- Variabel harus di-set terlebih dahulu sebelum digunakan dalam IF
"""
    
    print(panduan)

if __name__ == "__main__":
    main()
    panduan_penggunaan()