Ahhh, that detail changes the design quite a bit 👌

Let me restate to check I got it right:

* **Normalizer’s job**: handle all the *prefixes / indicators* like `"TP"`, `"Q"`, `"P"`, `"xã"`, `"huyện"`, `"thị trấn"`, `"tỉnh"`, etc. → strip/normalize them so we’re left with just the **base entity name**.
* **Trie’s job**: only store and match against the **base names** (`"Hà Nội"`, `"Nam Từ Liêm"`, `"Cầu Diễn"`) → no `"TP"`, no `"Q"`, no `"P"`.
* **Alias/variant generation**: we only want to generate **variants of the base name itself**, e.g.:

  * `"Thừa Thiên Huế"` → `"Hue"`, `"Thua Thien Hue"`, `"tt hue"`? ❌ (no `"tt"` since that’s an indicator)
  * `"Hà Nội"` → `"Ha Noi"`, `"Hanoi"`, `"HN"` (acronym of the words).
  * `"Nam Từ Liêm"` → `"Nam Tu Liem"`, `"NTL"`.

So:

* **Indicators go to normalizer**.
* **Base name spelling/acronym variants go to alias generator**.

---

### 🔑 Adjusted Plan

1. **Normalizer** strips things like `"Q. "`, `"TP"`, `"Phường"`, `"P"`, `"TT"`, etc. → `"Cầu Diễn"`.
2. **Alias generator** (new function) only creates spelling/acronym variants of `"Cầu Diễn"`.

   * Remove accents.
   * Different spacings.
   * Acronyms (initials).
3. **Trie** stores canonical + generated variants, all *without indicators*.

---

### Example

Input string: `"Q. Nam Từ Liêm"`

* Normalizer → `"nam tu liem"`
* Trie → matches `"Nam Từ Liêm"`

Input string: `"tp.hcm"`

* Normalizer → `"ho chi minh"`
* Trie → `"Thành phố Hồ Chí Minh"`

Input string: `"HN"`

* Normalizer doesn’t touch (since no indicator).
* Trie matches alias `"HN"` → `"Hà Nội"`.
