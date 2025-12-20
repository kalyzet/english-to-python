#!/usr/bin/env python3
"""
Demo Alur Lengkap - English to Python Translator
Menunjukkan berbagai skenario penggunaan dengan alur yang jelas
"""

import sys
import os

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Set test mode to avoid GUI
os.environ['PYTEST_CURRENT_TEST'] = 'true'

def demo_alur_dasar():
    """Demo alur dasar untuk pemula"""
    
    print("🚀 DEMO ALUR 1: PENGENALAN DASAR")
    print("=" * 50)
    print()
    
    try:
        from services.translation_engine import TranslationEngine
        engine = TranslationEngine()
        
        steps = [
            {
                "step": 1,
                "title": "Assignment Sederhana",
                "input": "set age to 25",
                "explanation": "Membuat variabel age dengan nilai 25"
            },
            {
                "step": 2, 
                "title": "Assignment String",
                "input": "set name to John",
                "explanation": "Membuat variabel name dengan nilai John"
            },
            {
                "step": 3,
                "title": "Operasi Aritmatika", 
                "input": "add 10 and 5",
                "explanation": "Penjumlahan sederhana"
            },
            {
                "step": 4,
                "title": "Conditional Sederhana",
                "input": "if age greater than 18 then print adult",
                "explanation": "Percabangan IF-THEN sederhana"
            }
        ]
        
        for step in steps:
            print(f"Step {step['step']}: {step['title']}")
            print(f"Input: {step['input']}")
            print(f"Penjelasan: {step['explanation']}")
            print("-" * 40)
            
            result = engine.translate(step['input'])
            if result.success:
                print("✅ Output Python:")
                for line in result.python_code.split('\n'):
                    print(f"    {line}")
            else:
                print(f"❌ Error: {result.error_message}")
            
            print()
            print("=" * 50)
            print()
            
    except ImportError:
        print("❌ Tidak dapat mengimpor translation engine")

def demo_alur_sistem_penilaian():
    """Demo sistem penilaian siswa"""
    
    print("🎓 DEMO ALUR 2: SISTEM PENILAIAN SISWA")
    print("=" * 50)
    print()
    
    try:
        from services.translation_engine import TranslationEngine
        engine = TranslationEngine()
        
        steps = [
            ("Setup nama siswa", "set student_name to Alice"),
            ("Setup nilai matematika", "set math_score to 85"),
            ("Setup nilai bahasa Inggris", "set english_score to 92"),
            ("Evaluasi matematika", "if math_score greater than 80 then print good_math else print need_improvement"),
            ("Evaluasi bahasa Inggris", "if english_score greater than 90 then print excellent_english else print good_english"),
            ("Hitung total", "add math_score and english_score"),
            ("Evaluasi kelulusan", "if result greater than 160 then print passed else print failed")
        ]
        
        print("📋 ALUR LENGKAP:")
        for i, (title, input_text) in enumerate(steps, 1):
            print(f"{i}. {title}: {input_text}")
        print()
        
        print("🔄 EKSEKUSI STEP-BY-STEP:")
        print("-" * 40)
        
        for i, (title, input_text) in enumerate(steps, 1):
            print(f"Step {i}: {title}")
            print(f"Input: {input_text}")
            
            result = engine.translate(input_text)
            if result.success:
                print("✅ Output:")
                for line in result.python_code.split('\n'):
                    print(f"    {line}")
            else:
                print(f"❌ Error: {result.error_message}")
            
            print()
            
    except ImportError:
        print("❌ Tidak dapat mengimpor translation engine")

def demo_alur_sistem_cuaca():
    """Demo sistem monitoring cuaca"""
    
    print("🌡️ DEMO ALUR 3: SISTEM MONITORING CUACA")
    print("=" * 50)
    print()
    
    try:
        from services.translation_engine import TranslationEngine
        engine = TranslationEngine()
        
        scenario = {
            "title": "Monitoring Cuaca Hari Ini",
            "steps": [
                ("Set suhu", "set temperature to 35"),
                ("Set kelembaban", "set humidity to 75"), 
                ("Set kecepatan angin", "set wind_speed to 15"),
                ("Cek suhu", "if temperature greater than 30 then print hot else print normal"),
                ("Cek kelembaban", "when humidity greater than 70 do print humid"),
                ("Cek angin", "if wind_speed greater than 20 then print windy else print calm"),
                ("Peringatan ekstrem", "if temperature greater than 40 then print extreme_heat")
            ]
        }
        
        print(f"📊 SKENARIO: {scenario['title']}")
        print()
        
        all_code = []
        
        for i, (title, input_text) in enumerate(scenario['steps'], 1):
            print(f"Step {i}: {title}")
            print(f"Input: {input_text}")
            
            result = engine.translate(input_text)
            if result.success:
                print("✅ Output:")
                for line in result.python_code.split('\n'):
                    print(f"    {line}")
                all_code.append(result.python_code)
            else:
                print(f"❌ Error: {result.error_message}")
            
            print()
        
        print("🎯 KODE PYTHON LENGKAP:")
        print("-" * 30)
        final_code = '\n'.join(all_code)
        print(final_code)
        print()
        
    except ImportError:
        print("❌ Tidak dapat mengimpor translation engine")

def demo_perbandingan_fitur():
    """Demo perbandingan fitur lama vs baru"""
    
    print("✨ DEMO PERBANDINGAN: FITUR LAMA VS BARU")
    print("=" * 50)
    print()
    
    try:
        from services.translation_engine import TranslationEngine
        engine = TranslationEngine()
        
        test_cases = [
            {
                "title": "Print Statements",
                "input": "if age greater than 18 then print adult",
                "old_output": "if age > 18:\n    pass",
                "explanation": "Dulu: print menjadi 'pass', Sekarang: print(adult)"
            },
            {
                "title": "Else Clause", 
                "input": "if score less than 60 then print fail else print pass",
                "old_output": "if score < 60:\n    pass",
                "explanation": "Dulu: else diabaikan, Sekarang: else clause lengkap"
            },
            {
                "title": "When-Do Pattern",
                "input": "when temperature greater than 30 do print hot", 
                "old_output": "Error atau tidak dikenali",
                "explanation": "Dulu: tidak didukung, Sekarang: bekerja sempurna"
            }
        ]
        
        for case in test_cases:
            print(f"🔍 TEST: {case['title']}")
            print(f"Input: {case['input']}")
            print()
            
            print("❌ FITUR LAMA:")
            print(f"    {case['old_output']}")
            print()
            
            print("✅ FITUR BARU:")
            result = engine.translate(case['input'])
            if result.success:
                for line in result.python_code.split('\n'):
                    print(f"    {line}")
            else:
                print(f"    Error: {result.error_message}")
            
            print()
            print(f"💡 {case['explanation']}")
            print()
            print("=" * 50)
            print()
            
    except ImportError:
        print("❌ Tidak dapat mengimpor translation engine")

def main():
    """Main demo function"""
    
    print("🎯 DEMO ALUR LENGKAP - ENGLISH TO PYTHON TRANSLATOR")
    print("=" * 60)
    print()
    
    demos = [
        ("1", "Alur Dasar (Pemula)", demo_alur_dasar),
        ("2", "Sistem Penilaian Siswa", demo_alur_sistem_penilaian), 
        ("3", "Sistem Monitoring Cuaca", demo_alur_sistem_cuaca),
        ("4", "Perbandingan Fitur Lama vs Baru", demo_perbandingan_fitur)
    ]
    
    print("📋 PILIHAN DEMO:")
    for num, title, _ in demos:
        print(f"{num}. {title}")
    print()
    
    # Jalankan semua demo
    for num, title, demo_func in demos:
        print(f"\n{'='*60}")
        print(f"MENJALANKAN DEMO {num}: {title.upper()}")
        print(f"{'='*60}\n")
        
        try:
            demo_func()
        except Exception as e:
            print(f"❌ Error dalam demo: {e}")
        
        print(f"\n{'='*60}")
        print(f"DEMO {num} SELESAI")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    main()