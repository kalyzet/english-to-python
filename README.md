# English to Python Translator (ttc)

Menerjemahkan kalimat bahasa Inggris terbatas (DSL sederhana) menjadi kode Python
yang valid dan bisa langsung dieksekusi — lewat **CLI Python** atau **GUI desktop
Rust (egui)**.

## Arsitektur

```
┌──────────────────────┐   JSON per baris (stdin/stdout)   ┌──────────────────────────┐
│  ttc-gui (Rust/egui) │ ◄──────────────────────────────► │  python -m ttc.worker     │
│  - panel input/UI    │   {"id":1,"cmd":"translate",...} │  - parser/generator/      │
│  - manajemen worker  │   {"id":1,"ok":true,...}         │    translator (ttc.*)     │
└──────────┬───────────┘   {"cmd":"input_request",...}    └────────────┬─────────────┘
           │ spawn + PYTHONPATH                    execute              │ subprocess
           ▼                                       (timeout)           ▼
   OS process worker                    ┌──────────────────────────────────────┐
                                        │ python -m ttc.runner (sandbox)       │
                                        │ - safe builtins, tanpa akses file    │
                                        │ - timeout → taskkill /T /F (pohon)   │
                                        └──────────────────────────────────────┘
```

- **GUI (Rust)** hanya antarmuka + manajemen proses worker. Tidak ada logika
  translasi di Rust.
- **Engine (Python)** memegang parser, generator, translator, sandbox, dan worker.
- Komunikasi GUI ↔ worker: JSON satu baris per pesan di stdin/stdout worker
  (logging worker hanya ke stderr). Protocol lengkap ada di
  `crates/ttc-gui/src/protocol.rs` dan `ttc/worker.py`.
- Eksekusi kode hasil translasi selalu lewat **subprocess terpisah** dengan
  timeout dan pembunuhan seluruh pohon proses (aman dari infinite loop).

## Pola yang didukung

| Pola | Contoh input | Hasil |
|---|---|---|
| Assignment | `set name to John` | `name = "John"` |
| Aritmatika | `add 10 and 5`, `multiply total by 0.1` | `result = 10 + 5`, `result = total * 0.1` |
| Kondisi | `if age greater than 18 then print adult` | `if age > 18:\n    print("adult")` |
| Kondisi lain | `when humidity greater than 70 do print humid` | `if humidity > 70:\n    print("humid")` |
| Loop | `repeat 3 times print hello`, `for each item in numbers print item`, `while x greater than 0 do print hi` | `for _ in range(3): ...`, dll. |
| Data | `create list with 1, 2, 3`, `add item to my_list` | `my_list = [...]`, `my_list.append("item")` |

Operator perbandingan: `greater than`/`is greater than` → `>`, `less than` → `<`,
`equals`/`is equal to` → `==`, plus varian `>=`, `<=`, `!=`.
Literal `true`/`false`/`none` di kondisi diterjemahkan ke `True`/`False`/`None`.

Panduan input step-by-step: [`docs/ALUR_CONTOH_INPUT.md`](docs/ALUR_CONTOH_INPUT.md).

## Persyaratan

- **Python >= 3.9** (dikembangkan & diuji di 3.13) — untuk engine dan CLI
- **Rust toolchain** — hanya untuk membangun GUI
- Install dependency dev Python:

  ```bash
  pip install -e .[dev]
  ```

## Cara menjalankan

### CLI

```bash
python -m ttc "set x to 5"           # terjemahkan, cetak kode Python
python -m ttc "repeat 3 times print hi" --run   # terjemahkan lalu eksekusi (sandbox)
```

`pip install -e .` juga mendaftarkan entry point `ttc`.

### GUI (egui)

```bash
cargo run --release          # dari root repo
# atau jalankan langsung:
target\release\ttc-gui.exe
```

GUI menemukan engine dengan mencari folder `ttc/__init__.py` ke atas dari lokasi
executable/cwd lalu menyetel `PYTHONPATH`. Override interpreter Python dengan
env `TTC_PYTHON` (mis. `TTC_PYTHON=python3.13`).

Alur di GUI: ketik kalimat → **Translate** → kode Python muncul → **Execute**
(jika kode meminta input, dialog input akan muncul) → output/evaluasi tampil.

## Pengujian

```bash
python -m pytest             # 192 test: unit + property + integration (~10 menit;
                             #   suite eksekusi property paling berat ~9 menit)
python -m pytest tests/unit              # hanya unit (cepat)
python -m pytest tests/integration       # protocol worker end-to-end

python -m mypy ttc           # strict type check

cargo test                   # 14 test Rust: serialisasi protocol + round-trip worker
cargo clippy --all-targets   # lint Rust (bersih)
cargo fmt --check            # format check Rust
```

Catatan: test eksekusi property menjalankan kode lewat subprocess sandbox dengan
timeout nyata, jadi wajar memakan waktu beberapa menit.

## Struktur proyek

```
text-to-code/
├── ttc/                     # Engine Python (package)
│   ├── __main__.py          # CLI: python -m ttc "..."
│   ├── engine/              # parser, generator, translator, literals, ...
│   ├── worker.py            # proses worker JSON (dipanggil GUI)
│   ├── runner.py            # child sandbox: builtins aman + input sentinel
│   ├── sandbox.py           # CodeExecutionService: subprocess + timeout kill
│   └── translator.py        # TranslationEngine, hasil & error handling
├── crates/ttc-gui/          # GUI Rust (eframe/egui 0.37)
│   └── src/
│       ├── main.rs          # entry point eframe
│       ├── app.rs           # state & panel GUI
│       ├── worker.rs        # spawn/kelola proses worker Python
│       └── protocol.rs      # tipe JSON wire protocol
├── tests/
│   ├── unit/                # unit test engine
│   ├── property/            # property-based tests (hypothesis)
│   └── integration/         # protokol worker end-to-end
├── docs/                    # panduan input
├── Cargo.toml               # workspace Rust
├── pyproject.toml           # package Python + dependency dev
└── pytest.ini / mypy.ini / conftest.py
```

## Lisensi

MIT License
