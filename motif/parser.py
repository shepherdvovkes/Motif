"""
MOTIF Language Parser
Implements a Lisp-like syntax parser for the MOTIF emotional programming language.
"""

import re
from typing import List, Dict, Any, Union, Optional
from dataclasses import dataclass
from enum import Enum
import ast


class TokenType(Enum):
    """Token types for MOTIF language"""
    LPAREN = "("
    RPAREN = ")"
    SYMBOL = "SYMBOL"
    STRING = "STRING"
    NUMBER = "NUMBER"
    COMMENT = "COMMENT"
    EOF = "EOF"


@dataclass
class Token:
    """Token representation"""
    type: TokenType
    value: str
    line: int
    column: int


class MOTIFLexer:
    """Lexer for MOTIF language with Lisp-like syntax"""
    
    def __init__(self, text: str):
        self.text = text
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
    
    def tokenize(self) -> List[Token]:
        """Tokenize the input text"""
        while self.position < len(self.text):
            self._skip_whitespace()
            if self.position >= len(self.text):
                break
            
            char = self.text[self.position]
            
            if char == '(':
                self._add_token(TokenType.LPAREN, char)
                self._advance()
            elif char == ')':
                self._add_token(TokenType.RPAREN, char)
                self._advance()
            elif char == '"':
                self._tokenize_string()
            elif char == ';':
                self._tokenize_comment()
            elif char.isdigit() or char == '-':
                self._tokenize_number()
            elif char.isalpha() or char in '-_':
                self._tokenize_symbol()
            else:
                self._advance()
        
        self._add_token(TokenType.EOF, "")
        return self.tokens
    
    def _skip_whitespace(self):
        """Skip whitespace characters"""
        while self.position < len(self.text) and self.text[self.position].isspace():
            if self.text[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def _tokenize_string(self):
        """Tokenize string literal"""
        start_pos = self.position
        self._advance()  # Skip opening quote
        
        while self.position < len(self.text) and self.text[self.position] != '"':
            if self.text[self.position] == '\\':
                self._advance()  # Skip escape character
            self._advance()
        
        if self.position < len(self.text):
            self._advance()  # Skip closing quote
        
        value = self.text[start_pos:self.position]
        self._add_token(TokenType.STRING, value)
        # Position already advanced in the while loop
    
    def _tokenize_comment(self):
        """Tokenize comment"""
        start_pos = self.position
        while self.position < len(self.text) and self.text[self.position] != '\n':
            self._advance()
        
        value = self.text[start_pos:self.position]
        self._add_token(TokenType.COMMENT, value)
        # Position already advanced in the while loop
    
    def _tokenize_number(self):
        """Tokenize number literal"""
        start_pos = self.position
        
        # Handle negative numbers
        if self.text[self.position] == '-':
            self._advance()
        
        while (self.position < len(self.text) and 
               (self.text[self.position].isdigit() or self.text[self.position] == '.')):
            self._advance()
        
        value = self.text[start_pos:self.position]
        self._add_token(TokenType.NUMBER, value)
        # Position already advanced in the while loop
    
    def _tokenize_symbol(self):
        """Tokenize symbol"""
        start_pos = self.position
        
        while (self.position < len(self.text) and 
               (self.text[self.position].isalnum() or 
                self.text[self.position] in '-_')):
            self._advance()
        
        value = self.text[start_pos:self.position]
        self._add_token(TokenType.SYMBOL, value)
        # Position already advanced in the while loop
    
    def _add_token(self, token_type: TokenType, value: str):
        """Add token to the list"""
        token = Token(token_type, value, self.line, self.column)
        self.tokens.append(token)
        # Don't advance here - let the caller handle position
    
    def _advance(self):
        """Advance position"""
        if self.position < len(self.text):
            self.position += 1
            self.column += 1


class MOTIFParser:
    """Parser for MOTIF language AST generation"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
    
    def parse(self) -> List[Any]:
        """Parse tokens into AST"""
        expressions = []
        
        while not self._is_at_end():
            if self._peek().type == TokenType.COMMENT:
                self._advance()  # Skip comments
                continue
            
            expr = self._parse_expression()
            if expr is not None:
                expressions.append(expr)
        
        return expressions
    
    def _parse_expression(self) -> Any:
        """Parse a single expression"""
        if self._peek().type == TokenType.LPAREN:
            return self._parse_list()
        elif self._peek().type == TokenType.STRING:
            return self._parse_string()
        elif self._peek().type == TokenType.NUMBER:
            return self._parse_number()
        elif self._peek().type == TokenType.SYMBOL:
            return self._parse_symbol()
        else:
            raise SyntaxError(f"Unexpected token: {self._peek().value}")
    
    def _parse_list(self) -> List[Any]:
        """Parse S-expression list"""
        self._consume(TokenType.LPAREN, "Expected '('")
        
        elements = []
        while not self._check(TokenType.RPAREN) and not self._is_at_end():
            if self._peek().type == TokenType.COMMENT:
                self._advance()  # Skip comments
                continue
            elements.append(self._parse_expression())
        
        self._consume(TokenType.RPAREN, "Expected ')'")
        return elements
    
    def _parse_string(self) -> str:
        """Parse string literal"""
        token = self._consume(TokenType.STRING, "Expected string")
        # Remove quotes
        return token.value[1:-1]
    
    def _parse_number(self) -> Union[int, float]:
        """Parse number literal"""
        token = self._consume(TokenType.NUMBER, "Expected number")
        try:
            if '.' in token.value:
                return float(token.value)
            else:
                return int(token.value)
        except ValueError:
            raise SyntaxError(f"Invalid number: {token.value}")
    
    def _parse_symbol(self) -> str:
        """Parse symbol"""
        token = self._consume(TokenType.SYMBOL, "Expected symbol")
        return token.value
    
    def _peek(self) -> Token:
        """Peek at current token"""
        if self.position >= len(self.tokens):
            return self.tokens[-1] if self.tokens else None
        return self.tokens[self.position]
    
    def _advance(self) -> Token:
        """Advance and return previous token"""
        if not self._is_at_end():
            self.position += 1
        return self.tokens[self.position - 1]
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """Consume token of expected type"""
        if self._check(token_type):
            return self._advance()
        raise SyntaxError(f"{message} at line {self._peek().line}, column {self._peek().column}")
    
    def _check(self, token_type: TokenType) -> bool:
        """Check if current token is of expected type"""
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _is_at_end(self) -> bool:
        """Check if at end of tokens"""
        return self.position >= len(self.tokens) or (self.tokens and self.tokens[self.position].type == TokenType.EOF)


class MOTIFAST:
    """AST node types for MOTIF language"""
    
    @dataclass
    class DefineArchetype:
        name: str
        properties: Dict[str, Any]
    
    @dataclass
    class DefineImage:
        name: str
        sensory_data: Dict[str, Any]
    
    @dataclass
    class DefineEmotion:
        name: str
        properties: Dict[str, Any]
    
    @dataclass
    class DefineMetaphor:
        name: str
        source: str
        target: str
        properties: Dict[str, Any]
    
    @dataclass
    class DefineMotif:
        name: str
        components: Dict[str, Any]
    
    @dataclass
    class DefineLeitmotif:
        name: str
        motifs: List[str]
        properties: Dict[str, Any]
    
    @dataclass
    class DefineComposition:
        name: str
        structure: Dict[str, Any]
    
    @dataclass
    class Compose:
        composition_name: str
    
    @dataclass
    class ExecuteMotif:
        motif_name: str
    
    @dataclass
    class GenerateEmotion:
        emotion_name: str
        intensity: float
    
    @dataclass
    class ApplyMetaphor:
        metaphor_name: str
        source: str
        target: str
    
    @dataclass
    class IfEmotionalState:
        condition: Any
        then_expr: Any
        else_expr: Any
    
    @dataclass
    class WhileEmotionalState:
        condition: Any
        body: List[Any]
    
    @dataclass
    class PredictEmotionalTriggers:
        target_emotion: str
        context: str
    
    @dataclass
    class OptimizeForImpact:
        composition_name: str
        target_emotion: str
    
    @dataclass
    class AnalyzeContext:
        context_types: List[str]
    
    @dataclass
    class GenerateSeedWords:
        emotion: str
        intensity: float
        context: str


class MOTIFInterpreter:
    """Interpreter for MOTIF language with ML integration"""
    
    def __init__(self):
        self.symbols = {}
        self.archetypes = {}
        self.emotions = {}
        self.metaphors = {}
        self.motifs = {}
        self.leitmotifs = {}
        self.compositions = {}
        self.context = {}
    
    def interpret(self, ast: List[Any]) -> Any:
        """Interpret AST and execute MOTIF program"""
        result = None
        
        for expression in ast:
            result = self._evaluate(expression)
        
        return result
    
    def _evaluate(self, expression: Any) -> Any:
        """Evaluate a single expression"""
        if isinstance(expression, list):
            return self._evaluate_list(expression)
        elif isinstance(expression, str):
            return self._evaluate_symbol(expression)
        elif isinstance(expression, (int, float)):
            return expression
        else:
            return expression
    
    def _evaluate_list(self, expression: List[Any]) -> Any:
        """Evaluate S-expression list"""
        if not expression:
            return None
        
        operator = expression[0]
        args = expression[1:]
        
        # Definition operators
        if operator == "define-archetype":
            return self._define_archetype(args)
        elif operator == "define-image":
            return self._define_image(args)
        elif operator == "define-emotion":
            return self._define_emotion(args)
        elif operator == "define-metaphor":
            return self._define_metaphor(args)
        elif operator == "define-motif":
            return self._define_motif(args)
        elif operator == "define-leitmotif":
            return self._define_leitmotif(args)
        elif operator == "define-composition":
            return self._define_composition(args)
        elif operator == "define-context":
            return self._define_context(args)
        elif operator == "define-seed-words":
            return self._define_seed_words(args)
        
        # Execution operators
        elif operator == "compose":
            return self._compose(args)
        elif operator == "execute-motif":
            return self._execute_motif(args)
        elif operator == "generate-emotion":
            return self._generate_emotion(args)
        elif operator == "apply-metaphor":
            return self._apply_metaphor(args)
        
        # Control flow
        elif operator == "if-emotional-state":
            return self._if_emotional_state(args)
        elif operator == "while-emotional-state":
            return self._while_emotional_state(args)
        elif operator == "listener-state":
            return self._listener_state(args)
        
        # ML integration
        elif operator == "predict-emotional-triggers":
            return self._predict_emotional_triggers(args)
        elif operator == "optimize-for-impact":
            return self._optimize_for_impact(args)
        elif operator == "analyze-context":
            return self._analyze_context(args)
        elif operator == "generate-seed-words":
            return self._generate_seed_words(args)
        
        else:
            raise RuntimeError(f"Unknown operator: {operator}")
    
    def _evaluate_symbol(self, symbol: str) -> Any:
        """Evaluate symbol reference"""
        if symbol in self.symbols:
            return self.symbols[symbol]
        elif symbol in self.archetypes:
            return self.archetypes[symbol]
        elif symbol in self.emotions:
            return self.emotions[symbol]
        elif symbol in self.metaphors:
            return self.metaphors[symbol]
        elif symbol in self.motifs:
            return self.motifs[symbol]
        elif symbol in self.leitmotifs:
            return self.leitmotifs[symbol]
        elif symbol in self.compositions:
            return self.compositions[symbol]
        else:
            return symbol  # Return as literal
    
    def _define_archetype(self, args: List[Any]) -> Any:
        """Define archetype"""
        if len(args) < 1:
            raise RuntimeError("define-archetype requires at least a name")
        
        name = args[0]
        properties = {}
        
        # Parse properties
        for i in range(1, len(args), 2):
            if i + 1 < len(args):
                prop_name = args[i]
                prop_value = args[i + 1]
                # Handle list keys properly
                if isinstance(prop_name, list):
                    prop_name = str(prop_name)
                properties[prop_name] = prop_value
        
        archetype = MOTIFAST.DefineArchetype(name, properties)
        self.archetypes[name] = archetype
        return archetype
    
    def _define_image(self, args: List[Any]) -> Any:
        """Define image"""
        if len(args) < 1:
            raise RuntimeError("define-image requires at least a name")
        
        name = args[0]
        sensory_data = {}
        
        # Parse sensory data
        for i in range(1, len(args), 2):
            if i + 1 < len(args):
                sense = args[i]
                data = args[i + 1]
                sensory_data[sense] = data
        
        image = MOTIFAST.DefineImage(name, sensory_data)
        self.symbols[name] = image
        return image
    
    def _define_emotion(self, args: List[Any]) -> Any:
        """Define emotion"""
        if len(args) < 1:
            raise RuntimeError("define-emotion requires at least a name")
        
        name = args[0]
        properties = {}
        
        # Parse properties
        for i in range(1, len(args), 2):
            if i + 1 < len(args):
                prop_name = args[i]
                prop_value = args[i + 1]
                # Handle case where prop_name is a list
                if isinstance(prop_name, list) and len(prop_name) > 0:
                    prop_name_str = prop_name[0]
                    properties[prop_name_str] = prop_value
                elif isinstance(prop_name, str):
                    properties[prop_name] = prop_value
        
        emotion = MOTIFAST.DefineEmotion(name, properties)
        self.emotions[name] = emotion
        return emotion
    
    def _define_metaphor(self, args: List[Any]) -> Any:
        """Define metaphor"""
        if len(args) < 3:
            raise RuntimeError("define-metaphor requires name, source, and target")
        
        name = args[0]
        source = args[1]
        target = args[2]
        properties = {}
        
        # Parse properties
        for i in range(3, len(args), 2):
            if i + 1 < len(args):
                prop_name = args[i]
                prop_value = args[i + 1]
                # Handle case where prop_name is a list
                if isinstance(prop_name, list) and len(prop_name) > 0:
                    prop_name_str = prop_name[0]
                    properties[prop_name_str] = prop_value
                elif isinstance(prop_name, str):
                    properties[prop_name] = prop_value
        
        metaphor = MOTIFAST.DefineMetaphor(name, source, target, properties)
        self.metaphors[name] = metaphor
        return metaphor
    
    def _define_motif(self, args: List[Any]) -> Any:
        """Define motif"""
        if len(args) < 1:
            raise RuntimeError("define-motif requires at least a name")
        
        name = args[0]
        components = {}
        
        # Parse components
        for i in range(1, len(args), 2):
            if i + 1 < len(args):
                comp_name = args[i]
                comp_value = args[i + 1]
                # Handle list values properly - convert to string if needed
                if isinstance(comp_name, list):
                    comp_name = str(comp_name)
                components[comp_name] = comp_value
        
        motif = MOTIFAST.DefineMotif(name, components)
        self.motifs[name] = motif
        return motif
    
    def _define_leitmotif(self, args: List[Any]) -> Any:
        """Define leitmotif"""
        if len(args) < 1:
            raise RuntimeError("define-leitmotif requires at least a name")
        
        name = args[0]
        motifs = []
        properties = {}
        
        # Parse motifs and properties
        for i in range(1, len(args), 2):
            if i + 1 < len(args):
                key = args[i]
                value = args[i + 1]
                # Handle case where key is a list (e.g., (motifs ...))
                if isinstance(key, list) and len(key) > 0:
                    key_name = key[0]
                    if key_name == "motifs":
                        motifs = key[1:] if len(key) > 1 else []
                    else:
                        properties[key_name] = value
                elif isinstance(key, str):
                    if key == "motifs":
                        motifs = value if isinstance(value, list) else [value]
                    else:
                        properties[key] = value
        
        leitmotif = MOTIFAST.DefineLeitmotif(name, motifs, properties)
        self.leitmotifs[name] = leitmotif
        return leitmotif
    
    def _define_composition(self, args: List[Any]) -> Any:
        """Define composition"""
        if len(args) < 1:
            raise RuntimeError("define-composition requires at least a name")
        
        name = args[0]
        structure = {}
        
        # Parse structure
        for i in range(1, len(args), 2):
            if i + 1 < len(args):
                key = args[i]
                value = args[i + 1]
                # Handle case where key is a list (e.g., (leitmotif name))
                if isinstance(key, list) and len(key) > 0:
                    key_name = key[0]
                    if len(key) > 1:
                        # The value is actually the second element of the key list
                        structure[key_name] = key[1]
                    else:
                        structure[key_name] = value
                elif isinstance(key, str):
                    structure[key] = value
        
        composition = MOTIFAST.DefineComposition(name, structure)
        self.compositions[name] = composition
        return composition
    
    def _compose(self, args: List[Any]) -> Any:
        """Execute composition and generate song text for Suno"""
        if len(args) < 1:
            raise RuntimeError("compose requires composition name")
        
        composition_name = args[0]
        if composition_name not in self.compositions:
            raise RuntimeError(f"Composition '{composition_name}' not defined")
        
        composition = self.compositions[composition_name]
        print(f"🎵 Composing: {composition_name}")
        print(f"📊 Structure: {composition.structure}")
        
        # Generate song text for Suno
        song_text = self._generate_suno_text(composition)
        
        print("\n" + "="*60)
        print("🎤 SONG TEXT FOR SUNO")
        print("="*60)
        print(song_text)
        print("="*60)
        
        return {"status": "composed", "composition": composition_name, "song_text": song_text}
    
    def _generate_suno_text(self, composition) -> str:
        """Generate song text in Suno format based on composition"""
        # Get the leitmotif from composition
        leitmotif_name = None
        if hasattr(composition, 'structure') and 'leitmotif' in composition.structure:
            leitmotif_name = composition.structure['leitmotif']
            # Handle case where leitmotif_name is a list
            if isinstance(leitmotif_name, list) and len(leitmotif_name) > 0:
                leitmotif_name = leitmotif_name[0]
        
        if not leitmotif_name or leitmotif_name not in self.leitmotifs:
            return "No leitmotif found for composition"
        
        leitmotif = self.leitmotifs[leitmotif_name]
        motifs = leitmotif.motifs if hasattr(leitmotif, 'motifs') else []
        
        # Generate lyrics based on motifs
        verses = []
        choruses = []
        bridges = []
        
        for motif_name in motifs:
            # Handle case where motif_name is a list
            if isinstance(motif_name, list):
                motif_name = str(motif_name[0]) if len(motif_name) > 0 else str(motif_name)
            
            if motif_name in self.motifs:
                motif = self.motifs[motif_name]
                lyrics = self._motif_to_lyrics(motif)
                
                # Categorize based on motif name and emotional target
                if 'verse' in motif_name.lower():
                    verses.append(lyrics)
                elif 'chorus' in motif_name.lower():
                    choruses.append(lyrics)
                elif 'bridge' in motif_name.lower():
                    bridges.append(lyrics)
                else:
                    verses.append(lyrics)  # Default to verse
        
        # Build song structure
        song_parts = []
        
        # Add verses
        for i, verse in enumerate(verses):
            song_parts.append(f"[Verse {i+1}]")
            song_parts.append(verse)
            song_parts.append("")
            
            # Add chorus after each verse
            if choruses:
                song_parts.append("[Chorus]")
                song_parts.append(choruses[0])
                song_parts.append("")
        
        # Add bridge
        if bridges:
            song_parts.append("[Bridge]")
            song_parts.append(bridges[0])
            song_parts.append("")
        
        # Final chorus
        if choruses:
            song_parts.append("[Chorus]")
            song_parts.append(choruses[0])
            song_parts.append("")
        
        return "\n".join(song_parts)
    
    def _motif_to_lyrics(self, motif) -> str:
        """Convert motif to lyrical text"""
        if not hasattr(motif, 'components'):
            return "No motif content found"
        
        components = motif.components
        archetypes = []
        metaphors = []
        
        # Extract archetypes and metaphors
        for key, value in components.items():
            if 'archetype' in str(key).lower():
                if isinstance(value, list):
                    archetypes.extend([str(v) for v in value])
                else:
                    archetypes.append(str(value))
            elif 'metaphor' in str(key).lower():
                if isinstance(value, list):
                    metaphors.extend([str(v) for v in value])
                else:
                    metaphors.append(str(value))
        
        # Clean up archetypes and metaphors (remove brackets and quotes)
        clean_archetypes = []
        for arch in archetypes:
            if isinstance(arch, str):
                clean_arch = arch.replace("'", "").replace("[", "").replace("]", "").replace(",", " ").strip()
                # Split by spaces and add individual words
                words = clean_arch.split()
                for word in words:
                    if word and word not in clean_archetypes:
                        clean_archetypes.append(word)
        
        clean_metaphors = []
        for meta in metaphors:
            if isinstance(meta, str):
                clean_meta = meta.replace("'", "").replace("[", "").replace("]", "").replace(",", " ").strip()
                # Split by spaces and add individual words
                words = clean_meta.split()
                for word in words:
                    if word and word not in clean_metaphors:
                        clean_metaphors.append(word)
        
        # Generate poetic lines based on archetypes and metaphors
        lines = []
        
        # Create verses based on archetypes
        if 'heart' in clean_archetypes and 'ocean' in clean_archetypes:
            lines.append("My heart is like an ocean")
            lines.append("Deep and vast, in endless motion")
            lines.append("Waves of love that never cease")
            lines.append("Bringing me both pain and peace")
        
        if 'photograph' in clean_archetypes and 'moonlight' in clean_archetypes:
            lines.append("In moonlight, I see your photograph")
            lines.append("Fading slowly, but I still laugh")
            lines.append("At the memories we made together")
            lines.append("That will last forever and ever")
        
        if 'autumn' in clean_archetypes:
            lines.append("Like autumn leaves, our love did fall")
            lines.append("But memories remain, through it all")
            lines.append("Golden moments in my mind")
            lines.append("A love that time could never bind")
        
        if 'goodbye' in clean_archetypes:
            lines.append("Goodbye, my love, goodbye")
            lines.append("Though we must part, I'll never die")
            lines.append("In the garden of my heart")
            lines.append("Your memory will always start")
        
        # Add metaphor-based lines
        if 'heart-ocean' in clean_metaphors:
            lines.append("Your love was deep as the endless sea")
            lines.append("Now I'm drowning in what used to be")
            lines.append("Waves of sorrow crash on shore")
            lines.append("But I'll love you forevermore")
        
        if 'fading-photograph' in clean_metaphors:
            lines.append("Time fades the colors of our past")
            lines.append("But the love we shared will always last")
            lines.append("In sepia tones and silver light")
            lines.append("Our love still shines so bright")
        
        if 'autumn-love' in clean_metaphors:
            lines.append("Like autumn leaves that gently fall")
            lines.append("Our love changed, that's all")
            lines.append("But beauty lies in every season")
            lines.append("And love needs no special reason")
        
        if 'moonlight-promises' in clean_metaphors:
            lines.append("Under moonlight we made our vows")
            lines.append("But time has broken all our bows")
            lines.append("Still the moon shines just the same")
            lines.append("And whispers your sweet name")
        
        # If no specific patterns found, create generic lines
        if not lines:
            if clean_archetypes:
                for i, archetype in enumerate(clean_archetypes[:2]):
                    if i == 0:
                        lines.append(f"In the {archetype} of my mind")
                        lines.append(f"I find peace of a different kind")
                    else:
                        lines.append(f"The {archetype} calls to me")
                        lines.append(f"Across the endless sea")
            else:
                lines.append("In the silence of the night")
                lines.append("I search for what was right")
                lines.append("Love and loss, hand in hand")
                lines.append("Walking through this endless land")
        
        return "\n".join(lines[:4])  # Limit to 4 lines per section
    
    def _execute_motif(self, args: List[Any]) -> Any:
        """Execute motif"""
        if len(args) < 1:
            raise RuntimeError("execute-motif requires motif name")
        
        motif_name = args[0]
        if motif_name not in self.motifs:
            raise RuntimeError(f"Motif '{motif_name}' not defined")
        
        motif = self.motifs[motif_name]
        print(f"🎼 Executing motif: {motif_name}")
        print(f"🧠 Components: {motif.components}")
        
        return {"status": "executed", "motif": motif_name}
    
    def _generate_emotion(self, args: List[Any]) -> Any:
        """Generate emotion"""
        if len(args) < 2:
            raise RuntimeError("generate-emotion requires emotion name and intensity")
        
        emotion_name = args[0]
        intensity = args[1]
        
        print(f"💭 Generating emotion: {emotion_name} (intensity: {intensity})")
        
        return {"status": "generated", "emotion": emotion_name, "intensity": intensity}
    
    def _apply_metaphor(self, args: List[Any]) -> Any:
        """Apply metaphor"""
        if len(args) < 3:
            raise RuntimeError("apply-metaphor requires metaphor name, source, and target")
        
        metaphor_name = args[0]
        source = args[1]
        target = args[2]
        
        print(f"🔗 Applying metaphor: {metaphor_name} ({source} -> {target})")
        
        return {"status": "applied", "metaphor": metaphor_name}
    
    def _if_emotional_state(self, args: List[Any]) -> Any:
        """Conditional emotional logic"""
        if len(args) < 3:
            raise RuntimeError("if-emotional-state requires condition, then, and else")
        
        condition = self._evaluate(args[0])
        then_expr = args[1]
        else_expr = args[2]
        
        # Simple condition evaluation (would be more sophisticated in real implementation)
        if condition:
            return self._evaluate(then_expr)
        else:
            return self._evaluate(else_expr)
    
    def _while_emotional_state(self, args: List[Any]) -> Any:
        """Iterative emotional building"""
        if len(args) < 2:
            raise RuntimeError("while-emotional-state requires condition and body")
        
        condition = args[0]
        body = args[1] if isinstance(args[1], list) else [args[1]]
        
        result = None
        while self._evaluate(condition):
            for expr in body:
                result = self._evaluate(expr)
        
        return result
    
    def _listener_state(self, args: List[Any]) -> Any:
        """Get listener state"""
        if len(args) < 1:
            raise RuntimeError("listener-state requires a state name")
        
        state_name = args[0]
        
        # Mock listener state (would be more sophisticated in real implementation)
        mock_states = {
            "melancholy": True,
            "joy": False,
            "nostalgia": True,
            "despair": False
        }
        
        return mock_states.get(state_name, False)
    
    def _predict_emotional_triggers(self, args: List[Any]) -> Any:
        """Predict emotional triggers using ML"""
        if len(args) < 2:
            raise RuntimeError("predict-emotional-triggers requires target emotion and context")
        
        target_emotion = args[0]
        context = args[1]
        
        print(f"🤖 Predicting emotional triggers for: {target_emotion}")
        print(f"🌍 Context: {context}")
        
        # Mock ML prediction (would integrate with actual ML models)
        predicted_triggers = ["night", "silence", "distance", "memory"]
        
        return {"status": "predicted", "triggers": predicted_triggers}
    
    def _optimize_for_impact(self, args: List[Any]) -> Any:
        """Optimize composition for emotional impact"""
        if len(args) < 2:
            raise RuntimeError("optimize-for-impact requires composition name and target emotion")
        
        composition_name = args[0]
        target_emotion = args[1]
        
        print(f"⚡ Optimizing {composition_name} for {target_emotion}")
        
        return {"status": "optimized", "composition": composition_name, "target": target_emotion}
    
    def _analyze_context(self, args: List[Any]) -> Any:
        """Analyze current context"""
        context_types = args if args else ["political", "cultural", "temporal"]
        
        print(f"🔍 Analyzing context: {context_types}")
        
        # Mock context analysis
        analysis = {
            "political": "global_uncertainty",
            "cultural": "western_contemporary",
            "temporal": "2024"
        }
        
        return {"status": "analyzed", "context": analysis}
    
    def _generate_seed_words(self, args: List[Any]) -> Any:
        """Generate seed words for emotional impact"""
        if len(args) < 3:
            raise RuntimeError("generate-seed-words requires emotion, intensity, and context")
        
        emotion = args[0]
        intensity = args[1]
        context = args[2]
        
        print(f"🌱 Generating seed words for {emotion} (intensity: {intensity})")
        
        # Mock seed word generation
        seed_words = ["hammer", "void", "echo", "resonance"]
        
        return {"status": "generated", "seed_words": seed_words}
    
    def _define_context(self, args: List[Any]) -> Any:
        """Define context"""
        if len(args) < 1:
            raise RuntimeError("define-context requires at least a name")
        
        name = args[0]
        properties = {}
        
        # Parse properties
        for i in range(1, len(args), 2):
            if i + 1 < len(args):
                prop_name = args[i]
                prop_value = args[i + 1]
                # Handle case where prop_name is a list
                if isinstance(prop_name, list) and len(prop_name) > 0:
                    prop_name_str = prop_name[0]
                    properties[prop_name_str] = prop_value
                elif isinstance(prop_name, str):
                    properties[prop_name] = prop_value
        
        context = {"name": name, "properties": properties}
        self.context[name] = context
        return context
    
    def _define_seed_words(self, args: List[Any]) -> Any:
        """Define seed words"""
        if len(args) < 1:
            raise RuntimeError("define-seed-words requires at least a name")
        
        name = args[0]
        # For now, just store the name and return mock seed words
        seed_words = ["night", "silence", "distance", "memory"]
        
        self.symbols[name] = seed_words
        return {"name": name, "words": seed_words}


def parse_motif(code: str) -> List[Any]:
    """Parse MOTIF code into AST"""
    lexer = MOTIFLexer(code)
    tokens = lexer.tokenize()
    parser = MOTIFParser(tokens)
    return parser.parse()


def interpret_motif(code: str) -> Any:
    """Parse and interpret MOTIF code"""
    ast = parse_motif(code)
    interpreter = MOTIFInterpreter()
    return interpreter.interpret(ast)


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Read from file
        with open(sys.argv[1], 'r') as f:
            motif_code = f.read()
    else:
        # Example MOTIF program
        motif_code = """
        ;; MOTIF Program: Basic Despair
        (define-archetype night (emotional-weight 0.9))
        (define-archetype street (emotional-weight 0.7))
        (define-archetype light (emotional-weight 0.6))
        (define-archetype pharmacy (emotional-weight 0.8))
        
        (define-motif core-assertion
            (archetypes (night street light pharmacy))
            (emotional-target melancholy)
            (intensity 0.9))
        
        (define-leitmotif main-loop
            (motifs (core-assertion))
            (repetition infinite))
        
        (define-composition despair
            (leitmotif main-loop)
            (structure single-motif)
            (target-emotion profound-melancholy))
        
        (compose despair)
        """
    
    result = interpret_motif(motif_code)
    print(f"\n🎵 MOTIF Program Result: {result}")
