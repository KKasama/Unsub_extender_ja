# Unsub Extender — Japanese Edition / 日本語版

[English](#english) | [日本語](#日本語)

> **Status / 状況**: Private repository. This modified version is shared with the original author for review.
> It is **not to be published or redistributed** until the original author (Eric Schares) has approved.
> 非公開リポジトリです。原作者（Eric Schares 氏）の確認と了承が得られるまで、公開・再配布しません。

---

## English

### About

This is a modified version of [**Unsub Extender**](https://github.com/eschares/unsub_extender) by Eric Schares (Iowa State University), a Streamlit web app that turns an [Unsub](https://unsub.org) journal-subscription export (.csv) into interactive Altair graphs with sidebar filters.

This edition adds a **Japanese user interface** and explanations, while keeping the original English interface available.
The original script `unsub_extender.py` is kept unchanged next to the new `unsub_extender_ja.py`.

### What is different from the original

- **Language switch** in the sidebar (日本語 / English). Most text is bilingual; the explanations under each graph are Japanese only.
- **Currency switch** (yen ¥ / US dollar $). This only changes the symbol and axis ranges; **no exchange-rate conversion** is done. The currency is not read from the file.
- **"How the numbers are calculated" (計算のしくみ)** section: a plain-language explanation of Unsub's values (usage, CPU, CPU rank, free %) and of this app's own Instant Fill % (IF%) calculation.
- **Explanation under every graph** (Japanese): what the graph shows, how to read it, how to use it.
- **Explanation under every sidebar filter**, with a live count of how many journals fit that condition.
- **Terminology aligned with Unsub's Japanese interface** (e.g. アクセス充足率 for Instant Fill, 利用単価 (CPU), PTA（契約終了後のアクセス権）).
- **Japanese subject names** in the subject graph (unknown names are shown as-is).
- **More robust CSV loading**: extra title lines above the header row (e.g. `export (1)`) are skipped, and a friendly message is shown when required columns are missing.
- Layout fixes so that text is not clipped when zooming a graph.
- The third-party web-analytics snippets (Clicky, StatCounter) of the original were **removed**.

### Requirements

- **Python 3.11** (Python 3.12 or newer cannot install the pinned pandas 1.5.3)
- Packages in `requirements.txt`

### Run

```bash
# macOS (Homebrew): brew install python@3.11
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run unsub_extender_ja.py
```

Open http://localhost:8501. Upload your Unsub export ("Export" → "Download as spreadsheet"), or use the bundled sample data (USD).

### Input file

Required columns (the default names in an Unsub export):
`title, downloads, citations, authorships, usage, subscription_cost, subscribed, cpu, cpu_rank, use_ill_percent, use_oa_percent, use_other_delayed_percent, use_subscription_percent, free_instant_usage_percent`.
The `subject` (or `era_subjects`) column is used for the subject graph.

The `subscribed` column controls the colors: `TRUE` (keep, blue), `FALSE` (cancel, red), `MAYBE` (think more, green), blank (undecided, grey).

### Files

| File | Description |
|---|---|
| `unsub_extender_ja.py` | Japanese / English edition (this project's main file) |
| `unsub_extender.py` | Original script, unchanged |
| `README_upstream.md` | Original README |
| `Unsub_export_example.csv` | Sample data from the original project (USD) |

### License and credits

Unsub Extender is © 2021 Eric Schares and licensed under the **GNU Affero General Public License v3.0** (see `LICENSE`).
This modified version is distributed under the same license. Modifications are described above and in the header of `unsub_extender_ja.py`.
If this application is offered to users over a network, the AGPL requires that the corresponding source code be made available to them.

Original project: https://github.com/eschares/unsub_extender
Paper: Schares, E. (2022). *Quantitative Science Studies*. https://doi.org/10.1162/qss_a_00200

---

## 日本語

### 概要

[Unsub](https://unsub.org) からエクスポートしたジャーナル購読の分析ファイル（.csv）を読み込み、絞り込みができる対話型グラフに変換する Streamlit アプリ、[**Unsub Extender**](https://github.com/eschares/unsub_extender)（作成：Eric Schares 氏、アイオワ州立大学）の改変版です。

元の英語画面を残したまま、**日本語の画面と解説**を追加しました。元のスクリプト `unsub_extender.py` は変更せず、日本語版 `unsub_extender_ja.py` を並べて置いています。

### 元のバージョンとの違い

- サイドバーに**言語の切り替え**（日本語 / English）を追加。画面の文言は日英両対応で、各グラフの下の解説は日本語のみです。
- **通貨の切り替え**（円 ¥ / ドル $）。切り替わるのは記号と軸の範囲だけで、**為替の換算はしません**。通貨はファイルから自動判別しません。
- 「**計算のしくみ**」欄を追加。Unsub が計算済みの値（利用量、利用単価（CPU）、CPUランク、フリー率）と、このアプリ自身が計算するアクセス充足率（IF%）を、やさしい言葉で説明しています。
- **各グラフの下に解説**（何を見るか、読み方、活用のしかた）を追加。
- **絞り込みの各項目の下に解説**を追加。その条件だけで何誌が残るかも、リアルタイムで表示します。
- 用語を **Unsub の日本語画面に合わせました**（アクセス充足率、利用単価（CPU）、PTA（契約終了後のアクセス権）など）。
- 分野（サブジェクト）のグラフで**日本語名**を表示（未登録の名前は、そのまま表示）。
- **CSV の読み込みを強化**：見出し行の上に余分なタイトル行（例：`export (1)`）があっても自動で読み飛ばし、必要な列が足りないときは分かりやすいメッセージを表示します。
- グラフを拡大したときに文字が切れる問題を修正。
- 元のアプリにあった外部のアクセス解析（Clicky、StatCounter）は**削除**しました。

### 必要な環境

- **Python 3.11**（Python 3.12 以降では、指定の pandas 1.5.3 をインストールできません）
- `requirements.txt` のパッケージ

### 起動のしかた

```bash
# macOS（Homebrew）の場合：brew install python@3.11
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run unsub_extender_ja.py
```

ブラウザで http://localhost:8501 を開き、Unsub の「エクスポート」→「スプレッドシートとしてダウンロード」で保存した .csv をアップロードします。何もアップロードしない場合は、付属のサンプルデータ（ドル建て）が表示されます。

### 入力ファイル

必要な列（Unsub のエクスポートの標準の列名）：
`title, downloads, citations, authorships, usage, subscription_cost, subscribed, cpu, cpu_rank, use_ill_percent, use_oa_percent, use_other_delayed_percent, use_subscription_percent, free_instant_usage_percent`
分野のグラフには `subject`（または `era_subjects`）列を使います。

`subscribed` 列は色分けに使われます：`TRUE`（購読継続・青）、`FALSE`（解約・赤）、`MAYBE`（要検討・緑）、空欄（未決定・灰色）。

### ファイル構成

| ファイル | 内容 |
|---|---|
| `unsub_extender_ja.py` | 日本語 / 英語版（このプロジェクトの本体） |
| `unsub_extender.py` | 元のスクリプト（変更なし） |
| `README_upstream.md` | 元の README |
| `Unsub_export_example.csv` | 元のプロジェクトのサンプルデータ（ドル建て） |

### ライセンスと謝辞

Unsub Extender は © 2021 Eric Schares による作品で、**GNU Affero General Public License v3.0**（`LICENSE` を参照）で提供されています。この改変版も、同じライセンスで提供します。改変内容は上記と、`unsub_extender_ja.py` の冒頭に記載しています。このアプリをネットワーク経由で利用者に提供する場合、AGPL により、対応するソースコードを利用者に提供する必要があります。

元のプロジェクト：https://github.com/eschares/unsub_extender
論文：Schares, E. (2022). *Quantitative Science Studies*. https://doi.org/10.1162/qss_a_00200
