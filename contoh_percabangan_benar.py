#!/usr/bin/env python3
"""
Contoh Percabangan BENAR - English to Python Translator
Menggunakan format yang sesuai dengan pattern yang didukung
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
    
    print("✅ === CONTOH PERCABANGAN YANG BENAR ===\n")
    
    # Berdasarkan error message, format yang benar adalah:
    # "if x greater than 5 then print yes"
    # "when count equals 0 do print empty"
    
    contoh_benar = [
        # 1. Setup variabel dulu
        ("🔧 Setup Variabel", [
            "set age to 20",
            "set score to 85", 
            "set temperature to 35",
            "set count to 0"
        ]),
        
        # 2. IF dengan THEN (format yang benar)
        ("🔀 IF dengan THEN", [
            "if age greater than 18 then print adult",
            "if score greater than 80 then print excellent", 
            "if temperature greater than 30 then print hot",
            "if count equals 0 then print empty"
        ]),
        
        # 3. WHEN dengan DO (format alternatif)
        ("🔄 WHEN dengan DO", [
            "when age greater than 25 do print mature",
            "when score equals 100 do print perfect",
            "when temperature less than 20 do print cold",
            "when count equals 0 do print zero"
        ]),
        
        # 4. IF dengan ELSE
        ("🔀 IF dengan ELSE", [
            "if age greater than 18 then print adult else print minor",
            "if score greater than 60 then print pass else print fail"
        ])
    ]
    
    for kategori, instruksi_list in contoh_benar:
        print(f"{kategori}:")
        print("-" * 50)
        
        for instruksi in instruksi_list:
            result = engine.translate(instruksi)
            
            print(f"📝 INPUT:  {instruksi}")
            
            if result.success:
                print(f"🐍 OUTPUT: {result.python_code}")
                
                # Tampilkan dengan indentasi yang benar
                if '\n' in result.python_code:
                    print("🐍 FORMATTED:")
                    lines = result.python_code.split('\n')
                    for line in lines:
                        print(f"          {line}")
                
                if result.warnings:
                    print(f"⚠️  WARNINGS: {len(result.warnings)} warning(s)")
            else:
                print(f"❌ ERROR: {result.error_message}")
            
            print()
        
        print()

def panduan_format_benar():
    print("📚 === PANDUAN FORMAT YANG BENAR ===\n")
    
    panduan = """
✅ FORMAT YANG DIDUKUNG:

1. IF dengan THEN:
   if [variabel] [operator] [nilai] then [aksi]
   
   Contoh:
   • if age greater than 18 then print adult
   • if score less than 60 then print fail
   • if count equals 0 then print empty

2. WHEN dengan DO:
   when [variabel] [operator] [nilai] do [aksi]
   
   Contoh:
   • when temperature greater than 30 do print hot
   • when status equals active do print running

3. IF dengan ELSE:
   if [variabel] [operator] [nilai] then [aksi1] else [aksi2]
   
   Contoh:
   • if age greater than 18 then print adult else print minor

🔧 OPERATOR YANG DIDUKUNG:
   • greater than  →  >
   • less than     →  <  
   • equals        →  ==

⚠️  PENTING:
   - HARUS ada kata "then" atau "do"
   - Tanpa "then/do" tidak akan dikenali sebagai conditional
   - Variabel harus sudah di-set sebelumnya

🎯 WORKFLOW YANG BENAR:
   1. set age to 20
   2. if age greater than 18 then print adult
   3. Translate & Run
"""
    
    print(panduan)

if __name__ == "__main__":
    main()
    panduan_format_benar()