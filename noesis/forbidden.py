"""Заборонені claims і евристика галюцинаційного ризику.

Жорстка межа продукту: ніколи не діагностувати, не лікувати, не замінювати
людське судження, не претендувати на AGI/свідомість.

Детектор стійкий до тривіальної обфускації, що оминала наївний підрядковий
матч (знайдено адверсаріальним самозламом v0.8):

* розрив сепараторами:  ``a g i`` / ``a.g.i`` / ``a-g-i`` ⟶ блок;
* кириличні гомогліфи:   ``АGI`` (кир. А) ⟶ блок;
* і дзеркальна хиба — підрядок ``agi`` всередині ``m·agi·c`` БІЛЬШЕ не
  спричиняє false-positive (межі слова для коротких ASCII-стемів).

Той самий нормалізатор застосовано і до маркерів надвпевненості
(``hallucination_risk``) — інакше ``г а р а н т о в а н о`` просочувався б
повз детектор (під-детекція = небезпечний напрям).

Залишкові відомі межі (поза можливостями стрічкового гейта, fail-closed —
радше зайва тривога, ніж пропуск): кирилічні стеми навмисно prefix-матч
(``діагност`` ловить і безпечну «діагностику трубопроводу»); агресивний
leetspeak з заміною кількох літер може просочитись; числа словами не ловляться.
"""

from __future__ import annotations

import re
import unicodedata

# (підрядок у нижньому регістрі, мітка порушення)
_FORBIDDEN_CLAIMS: tuple[tuple[str, str], ...] = (
    ("agi", "claim of AGI"),
    ("загальний штучний інтелект", "claim of AGI"),
    ("artificial general intelligence", "claim of AGI"),
    ("діагноз", "medical diagnosis"),
    ("діагност", "medical diagnosis"),
    ("вилікує", "healing claim"),
    ("вилікуємо", "healing claim"),
    ("зцілює", "healing claim"),
    ("психотерап", "therapy claim"),
    ("замінює лікаря", "replaces clinician"),
    ("замінює психолога", "replaces clinician"),
    ("замінює людське судження", "replaces human judgment"),
    ("фізично розширюємо свідомість", "consciousness expansion claim"),
    ("доведена модель мозку", "validated brain model claim"),
    ("науково валідована когнітивна", "validated cognitive-science claim"),
    # v0.4 / EIIC — нейрокогнітивні та екстрапольовані overclaims
    ("детектує свідомість", "consciousness detection"),
    ("вимірює свідомість", "consciousness measurement"),
    ("система свідома", "consciousness claim"),
    ("вимірює досвід", "IIT-experience overclaim"),
    ("доводить досвід", "IIT-experience overclaim"),
    ("судилось", "destiny language"),
    ("призначено долею", "destiny language"),
    ("така доля", "destiny language"),
    ("містичн", "mysticism"),
    ("езотер", "mysticism"),
    ("карма", "mysticism"),
)

# Двонапрямні confusable-пари кир.↔лат.: згортаємо ОБИДВІ сторони (текст і
# needle) одним відображенням до канонічного коду, тож наявні матчі лишаються
# незмінні, а гомогліф-атака на ASCII-needle ловиться. Канон — латиниця для
# літер, що мають латинський двійник.
_CONFUSABLES: dict[str, str] = {
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "х": "x",
    "і": "i", "ї": "i", "у": "y", "к": "k", "м": "m", "т": "t",
    "в": "b", "н": "h",
}
_FOLD = str.maketrans(_CONFUSABLES)

# Невидимі/нульової-ширини та bidi-керівні коди: візуально зникають, але рвуть
# токен, тож ``a​g​i`` оминало б детектор у динамічному середовищі
# (текст із довільних джерел). Видаляємо їх перед матчем.
_INVISIBLE = dict.fromkeys(
    [
        0x00AD,  # soft hyphen
        0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF,  # zero-width space/NJ/J/word-joiner/BOM
        0x200E, 0x200F,  # LTR/RTL marks
        0x202A, 0x202B, 0x202C, 0x202D, 0x202E,  # bidi embeddings/overrides
        0x2066, 0x2067, 0x2068, 0x2069,  # bidi isolates
    ],
    None,
)

# Між сусідніми символами needle дозволяємо «розривні» сепаратори (пробіли,
# крапки, дефіси, підкреслення, зірочки) — щоб ``a g i`` ⟶ ``agi``.
_SEP = r"[\s.\-_*]*"


def _normalize(text: str) -> str:
    """Канонізує Unicode-камуфляж до матчу (застосовується до needle і тексту).

    NFKC згортає fullwidth/сумісні форми (``ＡＧＩ`` ⟶ ``AGI``); прибираємо
    невидимі/bidi коди; NFD + видалення комбінувальних знаків знімає
    діакритичний камуфляж (``ági`` ⟶ ``agi``). Усе це знайдено
    екстраполяцією динамічних евазій safety-гейта.
    """
    text = unicodedata.normalize("NFKC", text).translate(_INVISIBLE)
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _fold(text: str) -> str:
    """Нормалізує Unicode, тоді згортає confusable-літери (needle і текст однаково)."""
    return _normalize(text).translate(_FOLD)


def _compile(needle: str) -> re.Pattern[str]:
    folded = _fold(needle)
    body = _SEP.join(re.escape(ch) for ch in folded)
    # Межі слова — лише для коротких ASCII-стемів (напр. ``agi``), щоб не ловити
    # підрядок усередині звичайних слів (``magic``). Кирилічні/довгі needle
    # лишаємо prefix/substring-матчем (навмисний стем «діагност» тощо).
    if len(folded) < 5 and folded.isascii() and folded.isalpha():
        body = r"(?<![0-9a-z])" + body + r"(?![0-9a-z])"
    return re.compile(body)


_COMPILED: tuple[tuple[re.Pattern[str], str], ...] = tuple(
    (_compile(needle), label) for needle, label in _FORBIDDEN_CLAIMS
)

# Маркери непідкріпленої впевненості (галюцинаційний ризик) — той самий
# нормалізатор, що й заборонені claims (стійкі до сепаратор-розриву/гомогліфів).
_CERTAINTY_MARKERS: tuple[str, ...] = (
    "гарантовано", "стовідсотково", "100% точно", "доведено науково",
    "завжди працює", "ніколи не помиляється", "guaranteed", "always works",
)
_CERTAINTY_COMPILED: tuple[tuple[re.Pattern[str], str], ...] = tuple(
    (_compile(marker), marker) for marker in _CERTAINTY_MARKERS
)

# Числа у виході. Захоплюємо згруповані (1 000 000) і десяткові (3.14) як цілий
# токен, щоб сигнал називав справжнє число, а не фрагмент («000»). Однозначні
# цілі навмисно НЕ ловимо (≈шум: «5 кроків», «у 3 етапи»).
_NUM = re.compile(r"\d{1,3}(?:[ ,]\d{3})+|\d+\.\d+|\d{2,}")


def check_forbidden_claims(text: str) -> list[str]:
    """Повертає список порушень заборонених claims; порожній = чисто.

    Стійкий до сепаратор-розриву та кириличних гомогліфів; без false-positive
    на коротких ASCII-стемах усередині звичайних слів.
    """
    folded = _fold(text.lower())
    return [label for pattern, label in _COMPILED if pattern.search(folded)]


def hallucination_risk(text: str, source: str = "") -> tuple[str, list[str]]:
    """Грубий ризик галюцинації: маркери надвпевненості + числа, відсутні у вході.

    Повертає (рівень, список_сигналів). Рівень ∈ {"low","medium","high"}.
    """
    folded = _fold(text.lower())
    signals = [marker for pattern, marker in _CERTAINTY_COMPILED if pattern.search(folded)]
    # Числа у виході, яких немає у вхідному джерелі — потенційна фабрикація.
    src_nums = set(_NUM.findall(source))
    out_nums = [n for n in _NUM.findall(text) if n not in src_nums]
    if out_nums:
        signals.append(f"числа без джерела: {', '.join(sorted(set(out_nums)))}")
    if len(signals) >= 2:
        return "high", signals
    if signals:
        return "medium", signals
    return "low", signals
