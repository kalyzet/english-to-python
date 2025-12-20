#!/usr/bin/env python3
"""
Demo Percabangan - English to Python Translator
Contoh input untuk conditional statements (if-then-else)
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from services.translation_engine import TranslationEngine

def demo_percabangan():
    """Demo berbagai jenis percabangan"""
    engine = TranslationEngine()
    
    print("🌟 === DEMO PERCABANGAN (CONDITIONAL STATEMENTS) ===\n")
    
    # Contoh percabangan yang didukung
    contoh_percabangan = [
        # 1. IF sederhana
        "if x greater than 5 then print hello",
        
        # 2. IF dengan ELSE
        "if age greater than 18 then print adult else print minor",
        
        # 3. IF dengan kondisi equals
        "if count equals 0 then print empty",
        
        # 4. IF dengan kondisi less than
        "if score less than 60 then print failed",
        
        # 5. WHEN (alternatif IF)
        "when temperature greater than 30 do print hot",
        
        # 6. WHEN dengan THEN
        "when user equals admin then print welcome",
        
        # 7. UNLESS (kondisi negatif)
        "unless password equals correct then print access denied",
        
        # 8. IF dengan multiple conditions (jika didukung)
        "if x greater than 0 then print positive else print negative"
    ]
    
    for i, instruction in enumerate(contoh_percabangan, 1):
        print(f"📝 {i}. INPUT:")
        print(f"   {instruction}")
        print(f"🐍 PYTHON OUTPUT:")
        
        result = engine.translate(instruction)
        
        if result.success:
            # Tampilkan kode dengan indentasi yang benar
            lines = result.python_code.split('\n')
            for line in lines:
                print(f"   {line}")
            
            # Tampilkan warnings jika ada
            if result.warnings:
                print(f"⚠️  WARNINGS:")
                for warning in result.warnings:
                    print(f"   - {warning}")
        else:
            print(f"❌ ERROR: {result.error_message}")
        
        print("-" * 60)
        print()

def demo_kombinasi_percabangan():
    """Demo kombinasi percabangan dengan assignment"""
    engine = TranslationEngine()
    
    print("🔥 === DEMO KOMBINASI PERCABANGAN + ASSIGNMENT ===\n")
    
    # Contoh kombinasi yang bisa dicoba satu per satu
    kombinasi = [
        # Setup variabel dulu
        "set age to 20",
        "set score to 85", 
        "set temperature to 35",
        
        # Kemudian percabangan
        "if age greater than 18 then print adult",
        "if score greater than 80 then print excellent",
        "if temperature greater than 30 then print hot weather"
    ]
    
    print("💡 CARA PENGGUNAAN:")
    print("   Masukkan instruksi ini satu per satu di aplikasi:\n")
    
    for i, instruction in enumerate(kombinasi, 1):
        print(f"{i}. {instruction}")
        
        # Terjemahkan untuk menunjukkan hasilnya
        result = engine.translate(instruction)
        if result.success:
            print(f"   → {result.python_code}")
        print()

if __name__ == "__main__":
    demo_percabangan()
    print("\n" + "="*60 + "\n")
    demo_kombinasi_percabangan()