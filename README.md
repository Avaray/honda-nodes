# honda-nodes

Paczka custom nodes dla [ComfyUI](https://github.com/comfyanonymous/ComfyUI).

Nody są pisane pod nowy **schemat V3** (`comfy_api.latest` / `io.ComfyNode`),
czyli API, na którym oparte jest nadchodzące **Nodes 2.0** (nowy,
Vue-owy silnik renderowania node'ów, obecnie dostępny jako opcjonalny
toggle w ustawieniach ComfyUI). Jednocześnie paczka **działa też na
obecnej wersji ComfyUI** — patrz sekcja [Architektura](#architektura-v1--v3)
poniżej.

## Instalacja

1. Skopiuj (lub `git clone`) folder `honda-nodes` do `ComfyUI/custom_nodes/`.
   Plik `__init__.py` musi leżeć bezpośrednio pod
   `ComfyUI/custom_nodes/honda-nodes/__init__.py` (bez podwójnego
   zagnieżdżenia folderu).
2. Zrestartuj ComfyUI.
3. Node pojawi się w menu "Add Node" w kategorii **Honda Nodes/Text**.

Brak zewnętrznych zależności Pythona — nie trzeba nic instalować przez pip.

## Nody

### Text Concatenate

Działa jak konsola DJ-a: node ma **kanały** — gniazda wejściowe, do
których podłącza się kable (STRING) z innych node'ów — a nie pola do
wpisywania tekstu. Łączy wartości ze wszystkich podłączonych kanałów w
jeden string, używając wskazanego łącznika, z opcjonalnym wymuszeniem
wielkości liter.

**Kanały (wejścia typu socket, nie widgety):**

- Node startuje z **jednym** pustym kanałem (`text_1`).
- Gdy podłączysz kabel do ostatniego (pustego) kanału, obok automatycznie
  pojawia się kolejny pusty kanał — i tak aż do 99 kanałów.
- Odłączenie kabla z ostatniego, pustego kanału z powrotem go chowa (do
  minimum jednego kanału). Odłączenie kanału **w środku** po prostu
  zostawia go pusty w miejscu — nic się nie przesuwa, wartość jest po
  prostu pomijana przy łączeniu (patrz `skip_empty` niżej).
- Kanały niczego nie "wyświetlają" poza samym faktem podłączenia — to
  zwykłe gniazda, żadnego wpisywania tekstu bezpośrednio w nodzie.

**Pozostałe inputy (to już zwykłe widgety):**

| Pole | Typ | Domyślnie | Opis |
|---|---|---|---|
| `case_mode` | combo | `Keep Original` | `Keep Original` / `UPPERCASE` / `lowercase` — wymusza wielkość liter na **końcowym, złączonym** stringu. |
| `separator` | string | `_` (underscore) | Łącznik wstawiany między poszczególne podłączone kanały. |
| `skip_empty` | boolean | `True` | Gdy włączone, kanały podłączone do pustego stringa (`""`) są pomijane przy łączeniu. Kanały w ogóle niepodłączone są pomijane zawsze, niezależnie od tego ustawienia. |

**Output:** `STRING` — złączony tekst, gotowy np. jako nazwa pliku, prompt
lub tag do przekazania dalej w grafie.

## Architektura: V1 / V3

Pakiet automatycznie wykrywa, czy zainstalowany ComfyUI obsługuje nowe
`comfy_api.latest` z `io.Autogrow` (wsparcie dla dynamicznych inputów w
schemacie V3 — dostępne w mainline ComfyUI mniej więcej od wersji 0.6.0,
styczeń 2026):

- **Jeśli tak (czyli w praktyce na każdej aktualnej instalacji ComfyUI)** —
  używana jest nowoczesna implementacja `honda_nodes/text_concatenate_v3.py`,
  oparta o `io.Schema` i `io.Autogrow.TemplatePrefix` z
  `force_input=True`. To jest **główna, docelowa wersja node'a**, gotowa
  pod Nodes 2.0, i to dokładnie ten sam wbudowany mechanizm, którego
  ComfyUI używa we własnym referencyjnym node'u testowym
  `AutogrowPrefixTestNode`.

- **Jeśli nie (starsza instalacja ComfyUI, bez API V3)** — używana jest
  klasyczna implementacja `honda_nodes/text_concatenate_v1.py`
  (`INPUT_TYPES` / `NODE_CLASS_MAPPINGS`, kanały jako opcjonalne
  `forceInput` STRING), wspierana przez skrypt
  `web/js/text_concatenate.js`, który ręcznie odtwarza zachowanie
  auto-rosnących kanałów (dodawanie/chowanie gniazd na podstawie
  podłączeń, `node.addInput` / `node.removeInput`).

Niezależnie od tego, która ścieżka jest aktywna, node zawsze rejestruje
się pod tym samym identyfikatorem (`Honda_TextConcatenate`) i nazwą
(„Text Concatenate") — dla użytkownika różnica jest niewidoczna.

## Rozwijanie paczki

Wspólna logika (case transform + łączenie tekstów) siedzi w
`honda_nodes/logic.py` i jest używana przez obie implementacje, żeby
zachowanie V1 i V3 zawsze było identyczne. Kolejne nody najlepiej dodawać
jako osobne pliki w `honda_nodes/`, rejestrując je:

- w V3 — dopisując klasę do listy w `HondaNodesExtension.get_node_list()`
  (`honda_nodes/text_concatenate_v3.py`),
- w V1 — dopisując wpis do `NODE_CLASS_MAPPINGS` /
  `NODE_DISPLAY_NAME_MAPPINGS` w odpowiednim pliku.

## Licencja

MIT — patrz [LICENSE](LICENSE).
