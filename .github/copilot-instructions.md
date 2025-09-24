# ASCII Dungeon PyGame - AI Coding Agent Instructions

## Architecture Overview

This is a **decoupled controller architecture** for a tile-based ASCII dungeon crawler. The main `Game` class orchestrates systems but delegates responsibilities to specialized controllers:

### Core Game Loop Pattern
```python
# game/game.py - Main orchestrator following this pattern:
events → InputHandler → Game._process_input_results() → controllers
continuous_input → Game._process_continuous_input() → Player.attempt_move()
Game._update_game_systems() → entities, camera, effects (only in PLAYING state)  
Game._process_floor_transitions() → transition_controller.apply_floor_transition()
Renderer.render_frame() → state-aware rendering (MAIN_MENU/PLAYING/PAUSED/GAME_OVER)
```

### Controller Pattern (Key Architectural Decision)
Recent refactoring extracted responsibilities from the monolithic `Game` class into stateless controllers:

- **`debug_controls.py`**: `toggle_debug_mode()`, `toggle_panel()` - F12 and 1-5 key handlers
- **`perf_controller.py`**: `log_performance_stats()` - performance monitoring every 300 frames  
- **`session_controller.py`**: `initialize_game_world()`, `restart_game()`, `start_game_if_needed()`
- **`audio_controller.py`**: `initialize_audio()`, `play_safe()` - sound loading and safe playback
- **`transition_controller.py`**: `apply_floor_transition()`, `log_transition_*()` - floor changes

**Pattern**: Controllers take dependencies as parameters (config, logger, game_state) rather than storing state.

## State Management Architecture

### GameStateEnum-Driven Flow
```python
# game/state.py
GameStateEnum: MAIN_MENU → PLAYING ⇄ PAUSED → GAME_OVER → RESTART → PLAYING
```

**Critical**: Input/update/rendering logic is **state-aware**:
- `InputHandler.handle_continuous_input()` returns empty dict if not PLAYING
- `Game._process_continuous_input()` and `_update_game_systems()` early-return if not PLAYING  
- `Renderer.render_frame()` dispatches to `_render_main_menu()`, `_render_game_over_screen()`, etc.

### Player Update Pattern
Player has **passive stamina regeneration** that must be paused during non-PLAYING states:
```python
# Only call player.passive_stamina_update(dt) when state == PLAYING
# This prevents stamina recovery during pause
```

## Data Flow & Resource Handling

### Relative Path Pattern
Resources use `os.path.join(os.path.dirname(__file__), '..', 'data', ...)` consistently:
```python
# game/utils.py - fonts/ directory scanning
# game/floors.py - data/enemies.json loading  
# game/state.py - logs/session/ writing
```

**PyInstaller Compatible**: Uses `--add-data "data;data"` to preserve relative structure.

### Level Generation Flow
```python
FloorManager.generate_level() → utils.generate_dungeon() → entities.json persistence
→ GameState.set_level() → GameState.compute_exit_pos() → renderer updates
```

## Key Development Patterns

### Error Handling Philosophy  
Uses **safe_call wrapper** pattern extensively:
```python
# game/game.py - Every major operation wrapped:
self.error_handler.safe_call(self._process_input_results, "input_processing", ...)
self.error_handler.safe_call(self.renderer.render_frame, "rendering", ...)
```

### Debug System Architecture
**F12** toggles `config.debug_mode` → enables **1-5 key panel toggles** → `renderer.debug_overlay` updates.
Debug panels: performance(1), game_state(2), player_state(3), entity_debug(4), logs(5).

### Experience System Integration
Player has **50-level progression** with `experience.py` bonus calculations:
```python
# Combat: player.gain_experience() → _apply_level_bonuses() → stamina/hp/speed updates
# Floor completion: automatic +40 XP with floating text notifications
```

## Critical Workflows

### Testing Strategy
```bash
# Unit tests (pygame-dependent, mock issues exist):
python tests/run_tests.py

# Non-graphical smoke test (preferred for CI):  
python tools/smoke_test.py

# Real-time debugging:
python tools/monitor_game_state.py
```

### Performance Monitoring
Built-in performance system logs every 300 frames:
```python
# Automatic warnings for >5% frame drops or >40ms frame time
# Debug-mode auto-optimization when performance degrades
```

### Packaging & Distribution
```bash
# One-command Windows packaging:  
powershell -ExecutionPolicy Bypass -File tools/package.ps1

# Includes data/, fonts/, docs/ via PyInstaller --add-data
```

## Common Patterns & Conventions

### Import Structure Philosophy
- Controllers import minimal dependencies and take parameters
- `game/` modules avoid circular imports via lazy imports (`from game.state import GameStateEnum`)
- Entry point: `main.py` → `Game()` → `game.run()`

### Floating Text Pattern
```python
# Use ui.py helpers consistently:
ui.add_floating_text(game_state, text, x, y, time_ms=700, damage=None)
ui.add_exp_text(game_state, f'+{exp} EXP', x, y)  
ui.add_levelup_text(game_state, f'LEVEL UP! Lv.{level}', x, y)
```

### FOV Integration Pattern  
```python
# player.py manages FOVSystem instance
# renderer.py checks player.is_tile_visible(x, y) for tile rendering
# Clear exploration on floor transitions via player.clear_exploration()
```

When adding features: follow the **controller extraction pattern** for complex logic, maintain **state-aware early returns**, and use the established **safe_call + logging** paradigm for error handling.