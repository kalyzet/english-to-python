#!/usr/bin/env python3
"""
Contoh Input Praktis untuk English to Python Translator
Jalankan file ini untuk melihat contoh-contoh input yang bisa digunakan
"""

def tampilkan_contoh_input():
    """Menampilkan berbagai contoh input yang bisa digunakan"""
    
    print("🎯 CONTOH INPUT UNTUK ENGLISH TO PYTHON TRANSLATOR")
    print("=" * 60)
    print()
    
    # Contoh Assignment
    print("📦 1. ASSIGNMENT VARIABEL")
    print("-" * 30)
    contoh_assignment = [
        "set age to 25",
        "set name to John", 
        "set score to 85.5",
        "set temperature to 30",
        "set status to active"
    ]
    
    for i, contoh in enumerate(contoh_assignment, 1):
        print(f"{i}. {contoh}")
    print()
    
    # Contoh Aritmatika
    print("🔢 2. OPERASI ARITMATIKA")
    print("-" * 30)
    contoh_aritmatika = [
        "add 10 and 5",
        "subtract 3 from 15", 
        "multiply 6 by 7",
        "divide 20 by 4",
        "calculate 25 plus 30"
    ]
    
    for i, contoh in enumerate(contoh_aritmatika, 1):
        print(f"{i}. {contoh}")
    print()
    
    # Contoh Conditional (BARU DIPERBAIKI!)
    print("🔀 3. CONDITIONAL STATEMENTS (BARU DIPERBAIKI!)")
    print("-" * 50)
    contoh_conditional = [
        "if age greater than 18 then print adult",
        "if score less than 60 then print fail",
        "when temperature greater than 30 do print hot",
        "if age greater than 18 then print adult else print minor",
        "if score greater than 80 then print excellent else print good"
    ]
    
    for i, contoh in enumerate(contoh_conditional, 1):
        print(f"{i}. {contoh}")
    print()
    
    # Workflow Lengkap
    print("🚀 4. WORKFLOW LENGKAP")
    print("-" * 25)
    print("Coba urutan input ini:")
    workflow = [
        "set age to 20",
        "set score to 85", 
        "if age greater than 18 then print adult",
        "if score greater than 80 then print excellent else print good",
        "when age equals 20 do print twenty"
    ]
    
    for i, step in enumerate(workflow, 1):
        print(f"{i}. {step}")
    print()
    
    print("💡 CARA MENGGUNAKAN:")
    print("1. Jalankan: python main.py")
    print("2. Masukkan salah satu contoh input di atas")
    print("3. Klik 'Translate' untuk melihat kode Python")
    print("4. Klik 'Run Code' untuk menjalankan kode")
    print()
    
    print("✨ FITUR BARU YANG SUDAH DIPERBAIKI:")
    print("✅ Print statements sekarang menghasilkan print() yang benar")
    print("✅ Else clause sudah fully implemented") 
    print("✅ Multiple conditional patterns (if-then, when-do)")
    print("✅ Deteksi otomatis string literal vs variabel")

def contoh_step_by_step():
    """Contoh step-by-step untuk dicoba"""
    
    print("\n" + "="*60)
    print("📋 CONTOH STEP-BY-STEP UNTUK DICOBA")
    print("="*60)
    
    scenarios = [
        {
            "title": "🎓 Scenario: Sistem Penilaian Siswa",
            "steps": [
                "set student_name to Alice",
                "set math_score to 85",
                "set english_score to 92", 
                "if math_score greater than 80 then print good_math",
                "if english_score greater than 90 then print excellent_english else print good_english"
            ]
        },
        {
            "title": "🌡️ Scenario: Sistem Monitoring Cuaca", 
            "steps": [
                "set temperature to 35",
                "set humidity to 75",
                "if temperature greater than 30 then print hot else print normal",
                "when humidity greater than 70 do print humid"
            ]
        },
        {
            "title": "👤 Scenario: Sistem Verifikasi Usia",
            "steps": [
                "set user_age to 17",
                "set has_permission to false",
                "if user_age greater than 18 then print adult else print minor", 
                "when has_permission equals true do print access_granted"
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['title']}")
        print("-" * 40)
        for i, step in enumerate(scenario['steps'], 1):
            print(f"{i}. {step}")
        print()

if __name__ == "__main__":
    tampilkan_contoh_input()
    contoh_step_by_step()
    
    print("\n🎉 SELAMAT MENCOBA!")
    print("Gunakan contoh-contoh di atas untuk menguji aplikasi English to Python Translator!")