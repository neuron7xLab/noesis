# ADAPTIVE_COMPRESSION

Виправляє padding-проблему v0.5. Фіксований Finalizer-100 → Finalizer-Adaptive.

## Режими (ComplexityProfile.recommended_output_mode)
micro 7–20 · brief 40–80 · standard 90–140 · deep 250–600 · protocol 1000+.
Короткий вхід → micro/brief; БЕЗ доповнення до 90–110.

## compression_status (чесний тег)
- `compressed` — вихід коротший за вхід (буває лише на довгих входах);
- `expanded_by_request` — довший, бо запитали deep/протокол (тег обов'язковий);
- `structured_not_compressed` — довший, але структурованіший (вхід <40 слів — виправдано);
- `failed_compression` — суттєвий вхід (≥40) став довшим без виправдання → Gate 1 FAIL.

## Чесний результат (100 входів)
`{structured_not_compressed: 100}` — на коротких/середніх входах система **структурує, не
стискає**, і КАЖЕ про це. Реальне стиснення — лише на довгих входах. Padding-брехня усунена.
