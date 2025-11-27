# Master Analysis Pipeline

## Übersicht

Vollständige Analyse-Pipeline für alle ~24.846 Seeds und Identities.

## Pipeline-Schritte

### Phase 1: Mapping (läuft gerade)
- `map_all_24846_seeds_to_real_ids.py`
- Erstellt Mapping zwischen Seeds und Real IDs

### Phase 2: Datenbank-Erstellung
- `create_complete_mapping_database.py`
- Erstellt vollständige Mapping-Datenbank
- **Input**: `complete_24846_seeds_to_real_ids_mapping.json`
- **Output**: `complete_mapping_database.json`

### Phase 3: Pattern-Analyse
- `analyze_documented_vs_real_patterns.py`
- Analysiert Patterns zwischen dokumentierten und realen IDs
- **Input**: `complete_mapping_database.json`
- **Output**: `documented_vs_real_pattern_analysis.json`

### Phase 4: Seed-Finding
- `find_seeds_for_fake_ids.py`
- Findet echte Seeds für dokumentierte IDs
- **Input**: `complete_mapping_database.json`
- **Output**: `seeds_for_fake_ids_analysis.json`

### Phase 5: Pattern Discovery
- `pattern_discovery_engine.py`
- Entdeckt Patterns und Muster
- **Input**: `complete_mapping_database.json`
- **Output**: `pattern_discovery_results.json`

### Phase 6: Statistische Analyse
- `statistical_analysis.py`
- Statistische Analysen
- **Input**: `complete_mapping_database.json`
- **Output**: `statistical_analysis_results.json`

### Phase 7: Code-Cracking
- `code_cracking_attempts.py`
- Versucht Code zu knacken
- **Input**: `complete_mapping_database.json`
- **Output**: `code_cracking_results.json`

### Phase 8: Neue Ideen
- `explore_new_ideas.py`
- Erkundet neue Ansätze
- **Input**: `complete_mapping_database.json`
- **Output**: `new_ideas_exploration.json`

## Ausführen

```bash
# Warte bis Mapping fertig ist, dann:
cd ${PROJECT_ROOT}

# Alle Analysen nacheinander:
python3 scripts/analysis/run_all_analyses.py

# Oder einzeln:
python3 scripts/analysis/create_complete_mapping_database.py
python3 scripts/analysis/analyze_documented_vs_real_patterns.py
python3 scripts/analysis/pattern_discovery_engine.py
python3 scripts/analysis/find_seeds_for_fake_ids.py
python3 scripts/analysis/statistical_analysis.py
python3 scripts/analysis/code_cracking_attempts.py
python3 scripts/analysis/explore_new_ideas.py
```

## Erwartete Erkenntnisse

1. **Pattern zwischen Fake und Real IDs**
2. **Layer-Zuordnungen**
3. **Transformation-Funktionen**
4. **Code-Knacken**
5. **Neue Türen und Ideen**
