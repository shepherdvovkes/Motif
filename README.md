# MOTIF: A Programming Language for Song Lyrics

MOTIF (Metaphorically Oriented Text Interpretation Framework) is a programming language that takes scripts in .motif format and generates song lyrics.

## 🎵 What MOTIF Does

MOTIF currently:
- **Takes .motif scripts** as input
- **Generates song lyrics** as output
- **Uses Lisp-like syntax** for defining musical motifs and compositions

## 📖 Language Syntax

MOTIF uses a Lisp-like syntax with S-expressions:

```motif
;; Define archetypal elements
(define-archetype night (emotional-weight 0.9) (cultural-context universal))
(define-archetype street (emotional-weight 0.7) (cultural-context urban-20th-century))

;; Create metaphors for emotional linking
(define-metaphor meaningless-light
    (source light)
    (target meaninglessness)
    (emotional-multiplier 1.3))

;; Define musical motifs
(define-motif core-assertion
    (archetypes (night street light pharmacy))
    (metaphors (meaningless-light))
    (emotional-target melancholy)
    (intensity 0.9))

;; Create compositions
(define-composition despair
    (leitmotif core-assertion)
    (target-emotion profound-melancholy))

;; Execute the composition
(compose despair)
```


## 📁 Project Structure

```
MOTIF/
├── MOTIF_SPECIFICATION.md    # Complete language specification
├── motif/
│   ├── parser.py            # Lisp-like parser and interpreter
│   ├── motif_cli.py         # CLI wrapper
│   └── simple_analyzer.py   # Simple text analyzer
├── examples/
│   ├── basic_despair.motif           # Simple melancholy example
│   ├── love_and_loss_song.motif     # Complex emotional composition
│   ├── ml_enhanced_nostalgia.motif  # ML-powered nostalgia
│   ├── context_aware_joy.motif      # Context-aware joy
│   └── absurdist_math_poem.motif    # Absurdist mathematical poem
├── motif_cli.py             # Main CLI interface
└── README.md               # This file
```

## 🚀 Quick Start

1. **Install Python 3.8+**
2. **Run the main example**:
   ```bash
   python3 motif_cli.py examples/absurdist_math_poem.motif
   ```

### Example Output:
```
А и Б сидели на трубе
А сидел уже давно и плотно
Б подсел только вчера
Но плотнее А на Икс в квадрате
На Икс в квадрате
экспоненциален
Икс в квадрате
не брит и брутален
экспоненциален
экспоненциален
экспоненциален
экспоненциален
```

## 🎯 Example Programs

### Basic Despair
```motif
;; Simple melancholy induction
(define-archetype night (emotional-weight 0.9))
(define-motif simple-sadness (archetypes (night)))
(define-composition hello-melancholy (leitmotif simple-sadness))
(compose hello-melancholy)
```

### А и Б сидели на трубе (Главный пример)
```motif
;; Простой пример абсурдистского математического стихотворения
;; Генерирует точный текст с математическими концепциями

(define-context russian-childhood
    (cultural-background russian)
    (emotional-theme playful-absurdity)
    (target-emotion amused-confusion))

;; Основные персонажи и математические концепции
(define-archetype A (emotional-weight 0.8) (cultural-context russian-childhood))
(define-archetype B (emotional-weight 0.8) (cultural-context russian-childhood))
(define-archetype x-squared (emotional-weight 0.9) (cultural-context mathematical))
(define-archetype exponential (emotional-weight 0.9) (cultural-context mathematical))

;; Мотивы для каждой строки
(define-motif line1
    (archetypes (A B pipe))
    (text-content "А и Б сидели на трубе"))

(define-motif line4
    (archetypes (B x-squared))
    (text-content "Но плотнее А на Икс в квадрате"))

;; Основная тема
(define-leitmotif main-theme
    (motifs (line1 line2 line3 line4 line5 line6 line7 line8 line9))
    (repetition single))

;; Финальная композиция
(define-composition absurdist-poem
    (leitmotif main-theme)
    (target-emotion amused-mathematical-confusion))

(compose absurdist-poem)
```

## 🔬 How It Works

MOTIF parses .motif files and generates lyrics based on:
- **Archetypes**: Universal symbols with emotional weight
- **Motifs**: Musical ideas and patterns
- **Compositions**: Complete song structures

## 📚 Documentation

- [Complete Language Specification](MOTIF_SPECIFICATION.md)
- [Example Programs](examples/)
- [Parser Implementation](motif/parser.py)

## 📄 License

MIT License - See LICENSE file for details

---

*MOTIF: A simple language for generating song lyrics from code.*
