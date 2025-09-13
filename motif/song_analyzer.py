"""
MOTIF Song Text Analyzer
Analyzes song lyrics and extracts emotional patterns, archetypes, and metaphors
to generate MOTIF code.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')


@dataclass
class EmotionalPattern:
    """Represents an emotional pattern found in song text"""
    emotion: str
    intensity: float
    keywords: List[str]
    context: str


@dataclass
class Archetype:
    """Represents an archetype found in song text"""
    name: str
    emotional_weight: float
    frequency: int
    context: str


@dataclass
class Metaphor:
    """Represents a metaphor found in song text"""
    source: str
    target: str
    emotional_multiplier: float
    confidence: float


class SongAnalyzer:
    """Analyzes song lyrics and extracts MOTIF components"""
    
    def __init__(self):
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set()
        
        # Emotional keyword mappings (English and Russian)
        self.emotion_keywords = {
            'love': ['love', 'heart', 'soul', 'passion', 'romance', 'beloved', 'darling', 'sweetheart',
                    'любовь', 'сердце', 'душа', 'страсть', 'романтика', 'любимый', 'дорогой'],
            'loss': ['goodbye', 'farewell', 'gone', 'lost', 'missing', 'empty', 'void', 'absence',
                    'прощай', 'ушел', 'потерян', 'пустота', 'отсутствие', 'исчез'],
            'melancholy': ['sad', 'blue', 'lonely', 'tears', 'cry', 'weep', 'sorrow', 'grief',
                          'грустно', 'одинокий', 'слезы', 'плакать', 'печаль', 'горе'],
            'nostalgia': ['memory', 'remember', 'past', 'yesterday', 'old', 'faded', 'photograph',
                         'память', 'вспоминать', 'прошлое', 'вчера', 'старый', 'фотография'],
            'hope': ['hope', 'dream', 'future', 'tomorrow', 'light', 'bright', 'shine',
                    'надежда', 'мечта', 'будущее', 'завтра', 'свет', 'яркий', 'сиять'],
            'despair': ['dark', 'night', 'end', 'death', 'die', 'broken', 'shattered',
                       'темный', 'ночь', 'конец', 'смерть', 'умереть', 'сломанный'],
            'joy': ['happy', 'smile', 'laugh', 'dance', 'sing', 'celebrate', 'joy', 'bliss',
                   'счастливый', 'улыбка', 'смех', 'танцевать', 'петь', 'радость'],
            'anger': ['angry', 'rage', 'fury', 'hate', 'burn', 'fire', 'storm', 'thunder',
                     'злой', 'ярость', 'ненависть', 'гореть', 'огонь', 'буря', 'гром'],
            'mathematical': ['квадрат', 'икс', 'экспонента', 'функция', 'математика', 'число',
                           'square', 'x', 'exponential', 'function', 'math', 'number']
        }
        
        # Archetype mappings (English and Russian)
        self.archetype_patterns = {
            'heart': ['heart', 'soul', 'spirit', 'core', 'center', 'сердце', 'душа', 'дух', 'центр'],
            'ocean': ['ocean', 'sea', 'waves', 'deep', 'vast', 'endless', 'океан', 'море', 'волны', 'глубокий'],
            'night': ['night', 'dark', 'moon', 'stars', 'midnight', 'evening', 'ночь', 'темный', 'луна', 'звезды'],
            'light': ['light', 'sun', 'bright', 'shine', 'glow', 'beam', 'свет', 'солнце', 'яркий', 'сиять'],
            'autumn': ['autumn', 'fall', 'leaves', 'golden', 'harvest', 'осень', 'листья', 'золотой', 'урожай'],
            'winter': ['winter', 'snow', 'cold', 'ice', 'frozen', 'зима', 'снег', 'холод', 'лед'],
            'spring': ['spring', 'bloom', 'flower', 'new', 'fresh', 'green', 'весна', 'цветок', 'новый', 'свежий'],
            'summer': ['summer', 'warm', 'hot', 'sunshine', 'beach', 'лето', 'теплый', 'жаркий', 'пляж'],
            'street': ['street', 'road', 'path', 'way', 'journey', 'улица', 'дорога', 'путь', 'путешествие'],
            'home': ['home', 'house', 'door', 'window', 'roof', 'дом', 'дверь', 'окно', 'крыша'],
            'sky': ['sky', 'heaven', 'clouds', 'blue', 'infinite', 'небо', 'облака', 'синий', 'бесконечный'],
            'fire': ['fire', 'flame', 'burn', 'spark', 'ember', 'огонь', 'пламя', 'гореть', 'искра'],
            'water': ['water', 'rain', 'river', 'stream', 'drop', 'вода', 'дождь', 'река', 'ручей', 'капля'],
            'wind': ['wind', 'breeze', 'air', 'blow', 'whisper', 'ветер', 'воздух', 'дуть', 'шепот'],
            'tree': ['tree', 'forest', 'wood', 'branch', 'root', 'дерево', 'лес', 'ветка', 'корень'],
            'bird': ['bird', 'fly', 'wing', 'feather', 'song', 'птица', 'летать', 'крыло', 'перо', 'песня'],
            'photograph': ['photo', 'picture', 'image', 'memory', 'frame', 'фото', 'картинка', 'память', 'рамка'],
            'music': ['song', 'music', 'melody', 'rhythm', 'harmony', 'песня', 'музыка', 'мелодия', 'ритм'],
            'dance': ['dance', 'move', 'step', 'sway', 'twirl', 'танец', 'двигаться', 'шаг', 'кружиться'],
            'time': ['time', 'moment', 'hour', 'day', 'year', 'forever', 'время', 'момент', 'час', 'день', 'год'],
            'mathematical': ['square', 'x', 'exponential', 'function', 'math', 'number', 'квадрат', 'икс', 'экспонента', 'функция', 'математика', 'число'],
            'pipe': ['pipe', 'tube', 'труба', 'трубка'],
            'sitting': ['sit', 'sitting', 'сидеть', 'сидящий']
        }
        
        # Metaphor patterns (English and Russian)
        self.metaphor_patterns = [
            (r'(\w+)\s+is\s+like\s+(\w+)', 'simile'),
            (r'(\w+)\s+as\s+(\w+)', 'simile'),
            (r'my\s+(\w+)\s+is\s+a\s+(\w+)', 'metaphor'),
            (r'(\w+)\s+of\s+(\w+)', 'metaphor'),
            (r'(\w+)\s+like\s+(\w+)', 'simile'),
            # Russian patterns
            (r'(\w+)\s+как\s+(\w+)', 'simile'),
            (r'(\w+)\s+словно\s+(\w+)', 'simile'),
            (r'(\w+)\s+будто\s+(\w+)', 'simile'),
            (r'(\w+)\s+на\s+(\w+)', 'metaphor'),
            (r'(\w+)\s+в\s+(\w+)', 'metaphor')
        ]
    
    def analyze_song(self, song_text: str) -> Dict[str, Any]:
        """Analyze song text and extract MOTIF components"""
        # Clean and preprocess text
        cleaned_text = self._clean_text(song_text)
        
        # Extract song structure
        structure = self._extract_structure(song_text)
        
        # Extract emotional patterns
        emotions = self._extract_emotions(cleaned_text)
        
        # Extract archetypes
        archetypes = self._extract_archetypes(cleaned_text)
        
        # Extract metaphors
        metaphors = self._extract_metaphors(cleaned_text)
        
        # Determine overall theme
        theme = self._determine_theme(emotions, archetypes)
        
        return {
            'structure': structure,
            'emotions': emotions,
            'archetypes': archetypes,
            'metaphors': metaphors,
            'theme': theme,
            'original_text': song_text
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess song text"""
        # Remove section markers like [Verse], [Chorus], etc.
        text = re.sub(r'\[.*?\]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Convert to lowercase
        text = text.lower()
        
        return text.strip()
    
    def _extract_structure(self, text: str) -> Dict[str, List[str]]:
        """Extract song structure from text"""
        structure = {
            'verses': [],
            'choruses': [],
            'bridges': [],
            'outros': []
        }
        
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section markers
            if line.startswith('[') and line.endswith(']'):
                # Save previous section
                if current_section and current_content:
                    structure[current_section].append('\n'.join(current_content))
                
                # Start new section
                section_name = line[1:-1].lower()
                if 'verse' in section_name or 'куплет' in section_name:
                    current_section = 'verses'
                elif 'chorus' in section_name or 'припев' in section_name:
                    current_section = 'choruses'
                elif 'bridge' in section_name or 'мост' in section_name:
                    current_section = 'bridges'
                elif 'outro' in section_name or 'концовка' in section_name:
                    current_section = 'outros'
                else:
                    current_section = 'verses'  # Default
                
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            structure[current_section].append('\n'.join(current_content))
        
        return structure
    
    def _extract_emotions(self, text: str) -> List[EmotionalPattern]:
        """Extract emotional patterns from text"""
        emotions = []
        words = word_tokenize(text)
        
        for emotion, keywords in self.emotion_keywords.items():
            matches = [word for word in words if word in keywords]
            if matches:
                intensity = min(len(matches) / len(keywords), 1.0)
                emotions.append(EmotionalPattern(
                    emotion=emotion,
                    intensity=intensity,
                    keywords=matches,
                    context=text
                ))
        
        return emotions
    
    def _extract_archetypes(self, text: str) -> List[Archetype]:
        """Extract archetypes from text"""
        archetypes = []
        words = word_tokenize(text)
        word_freq = Counter(words)
        
        for archetype, patterns in self.archetype_patterns.items():
            matches = [word for word in words if word in patterns]
            if matches:
                frequency = sum(word_freq[word] for word in matches)
                emotional_weight = min(frequency / 10.0, 1.0)
                
                archetypes.append(Archetype(
                    name=archetype,
                    emotional_weight=emotional_weight,
                    frequency=frequency,
                    context=text
                ))
        
        return archetypes
    
    def _extract_metaphors(self, text: str) -> List[Metaphor]:
        """Extract metaphors from text"""
        metaphors = []
        
        for pattern, metaphor_type in self.metaphor_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                source = match.group(1)
                target = match.group(2)
                
                # Calculate confidence based on pattern type
                confidence = 0.8 if metaphor_type == 'metaphor' else 0.6
                
                metaphors.append(Metaphor(
                    source=source,
                    target=target,
                    emotional_multiplier=1.2,
                    confidence=confidence
                ))
        
        return metaphors
    
    def _determine_theme(self, emotions: List[EmotionalPattern], archetypes: List[Archetype]) -> str:
        """Determine overall theme of the song"""
        if not emotions:
            return "neutral"
        
        # Find dominant emotion
        dominant_emotion = max(emotions, key=lambda e: e.intensity)
        
        # Map to theme
        theme_mapping = {
            'love': 'romantic-love',
            'loss': 'love-and-loss',
            'melancholy': 'existential-despair',
            'nostalgia': 'nostalgic-reflection',
            'hope': 'hopeful-optimism',
            'despair': 'profound-melancholy',
            'joy': 'celebration',
            'anger': 'passionate-anger',
            'mathematical': 'mathematical-poetry'
        }
        
        return theme_mapping.get(dominant_emotion.emotion, 'emotional-expression')


class MotifGenerator:
    """Generates MOTIF code from analyzed song data"""
    
    def __init__(self):
        self.context_counter = 0
        self.motif_counter = 0
        self.archetype_counter = 0
        self.metaphor_counter = 0
    
    def generate_motif_code(self, analysis: Dict[str, Any]) -> str:
        """Generate MOTIF code from song analysis"""
        lines = []
        
        # Add header comment
        lines.append(f";; MOTIF Program: Generated from Song Analysis")
        lines.append(f";; Theme: {analysis['theme']}")
        lines.append(f";; Generated by MOTIF Reverse Compiler")
        lines.append("")
        
        # Generate context
        context_name = self._generate_context(analysis, lines)
        
        # Generate archetypes
        archetype_names = self._generate_archetypes(analysis['archetypes'], lines)
        
        # Generate metaphors
        metaphor_names = self._generate_metaphors(analysis['metaphors'], lines)
        
        # Generate motifs for each section
        motif_names = self._generate_motifs(analysis, archetype_names, metaphor_names, lines)
        
        # Generate leitmotif
        leitmotif_name = self._generate_leitmotif(motif_names, lines)
        
        # Generate composition
        composition_name = self._generate_composition(leitmotif_name, analysis['theme'], lines)
        
        # Add compose command
        lines.append(f"(compose {composition_name})")
        
        return '\n'.join(lines)
    
    def _generate_context(self, analysis: Dict[str, Any], lines: List[str]) -> str:
        """Generate context definition"""
        self.context_counter += 1
        context_name = f"generated-context-{self.context_counter}"
        
        lines.append(f"(define-context {context_name}")
        lines.append(f"    (cultural-background universal)")
        lines.append(f"    (emotional-theme {analysis['theme']})")
        lines.append(f"    (temporal-context timeless))")
        lines.append("")
        
        return context_name
    
    def _generate_archetypes(self, archetypes: List[Archetype], lines: List[str]) -> List[str]:
        """Generate archetype definitions"""
        archetype_names = []
        
        for archetype in archetypes[:10]:  # Limit to top 10
            self.archetype_counter += 1
            archetype_name = f"archetype-{self.archetype_counter}"
            archetype_names.append(archetype_name)
            
            lines.append(f"(define-archetype {archetype_name}")
            lines.append(f"    (emotional-weight {archetype.emotional_weight:.1f})")
            lines.append(f"    (cultural-context universal))")
        
        if archetype_names:
            lines.append("")
        
        return archetype_names
    
    def _generate_metaphors(self, metaphors: List[Metaphor], lines: List[str]) -> List[str]:
        """Generate metaphor definitions"""
        metaphor_names = []
        
        for metaphor in metaphors[:5]:  # Limit to top 5
            self.metaphor_counter += 1
            metaphor_name = f"metaphor-{self.metaphor_counter}"
            metaphor_names.append(metaphor_name)
            
            lines.append(f"(define-metaphor {metaphor_name}")
            lines.append(f"    (source {metaphor.source})")
            lines.append(f"    (target {metaphor.target})")
            lines.append(f"    (emotional-multiplier {metaphor.emotional_multiplier:.1f})")
            lines.append(f"    (cultural-resonance high))")
        
        if metaphor_names:
            lines.append("")
        
        return metaphor_names
    
    def _generate_motifs(self, analysis: Dict[str, Any], archetype_names: List[str], 
                        metaphor_names: List[str], lines: List[str]) -> List[str]:
        """Generate motif definitions for each song section"""
        motif_names = []
        structure = analysis['structure']
        
        # Generate motifs for verses
        for i, verse in enumerate(structure['verses']):
            self.motif_counter += 1
            motif_name = f"verse-motif-{self.motif_counter}"
            motif_names.append(motif_name)
            
            lines.append(f"(define-motif {motif_name}")
            lines.append(f"    (archetypes ({' '.join(archetype_names[:3])}))")
            if metaphor_names:
                lines.append(f"    (metaphors ({' '.join(metaphor_names[:2])}))")
            lines.append(f"    (emotional-target {analysis['theme']})")
            lines.append(f"    (intensity 0.7)")
            lines.append(f"    (repetition-pattern gentle))")
            lines.append("")
        
        # Generate motifs for choruses
        for i, chorus in enumerate(structure['choruses']):
            self.motif_counter += 1
            motif_name = f"chorus-motif-{self.motif_counter}"
            motif_names.append(motif_name)
            
            lines.append(f"(define-motif {motif_name}")
            lines.append(f"    (archetypes ({' '.join(archetype_names[:4])}))")
            if metaphor_names:
                lines.append(f"    (metaphors ({' '.join(metaphor_names)}))")
            lines.append(f"    (emotional-target {analysis['theme']})")
            lines.append(f"    (intensity 0.9)")
            lines.append(f"    (repetition-pattern building))")
            lines.append("")
        
        # Generate motifs for bridges
        for i, bridge in enumerate(structure['bridges']):
            self.motif_counter += 1
            motif_name = f"bridge-motif-{self.motif_counter}"
            motif_names.append(motif_name)
            
            lines.append(f"(define-motif {motif_name}")
            lines.append(f"    (archetypes ({' '.join(archetype_names[:2])}))")
            lines.append(f"    (emotional-target {analysis['theme']})")
            lines.append(f"    (intensity 0.6)")
            lines.append(f"    (repetition-pattern single))")
            lines.append("")
        
        return motif_names
    
    def _generate_leitmotif(self, motif_names: List[str], lines: List[str]) -> str:
        """Generate leitmotif definition"""
        leitmotif_name = "main-theme"
        
        lines.append(f"(define-leitmotif {leitmotif_name}")
        lines.append(f"    (motifs ({' '.join(motif_names)}))")
        lines.append(f"    (repetition infinite)")
        lines.append(f"    (emotional-progression building))")
        lines.append("")
        
        return leitmotif_name
    
    def _generate_composition(self, leitmotif_name: str, theme: str, lines: List[str]) -> str:
        """Generate composition definition"""
        composition_name = "generated-composition"
        
        lines.append(f"(define-composition {composition_name}")
        lines.append(f"    (leitmotif {leitmotif_name})")
        lines.append(f"    (structure verse-chorus-bridge)")
        lines.append(f"    (target-emotion {theme}))")
        lines.append("")
        
        return composition_name


def analyze_song_to_motif(song_text: str) -> str:
    """Main function to convert song text to MOTIF code"""
    analyzer = SongAnalyzer()
    generator = MotifGenerator()
    
    # Analyze the song
    analysis = analyzer.analyze_song(song_text)
    
    # Generate MOTIF code
    motif_code = generator.generate_motif_code(analysis)
    
    return motif_code


# Example usage
if __name__ == "__main__":
    sample_song = """
[Verse 1]
In the silence of the night
I search for what was right
Love and loss, hand in hand
Walking through this endless land

[Chorus]
My heart is like an ocean
Deep and vast, in endless motion
Waves of love that never cease
Bringing me both pain and peace

[Verse 2]
Like autumn leaves, our love did fall
But memories remain, through it all
Golden moments in my mind
A love that time could never bind

[Chorus]
My heart is like an ocean
Deep and vast, in endless motion
Waves of love that never cease
Bringing me both pain and peace
"""
    
    motif_code = analyze_song_to_motif(sample_song)
    print(motif_code)