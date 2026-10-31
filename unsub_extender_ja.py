# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 21:16:06 2021

@author: eschares

--------------------------------------------------------------------------
Modified version: Japanese / English language switch added.
Original work: Unsub Extender, Copyright (c) 2021 Eric Schares
               https://github.com/eschares/unsub_extender
This modified version is an unofficial derivative and is distributed under
the same license as the original (GNU AGPL v3). See LICENSE.
Modifications: UI text and chart labels can be switched between Japanese and
English (function L() below); the third-party analytics snippets were removed.
--------------------------------------------------------------------------
"""
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import altair as alt
import os
import re
from datetime import datetime

st.set_page_config(page_title='Unsub Extender', page_icon="scissors.jpg", layout='centered', initial_sidebar_state="expanded")

# ---- Language switch (日本語 / English) ----
lang = st.sidebar.radio('言語 / Language', ['日本語', 'English'], key='lang')

def L(en, ja):
    """Return the Japanese or English string depending on the sidebar switch."""
    return ja if lang == '日本語' else en

# Labels reused in several places
SUB_TITLE = L('subscribed', '購読')
LINK_COLS = {} if lang != '日本語' else {'downloads': 'ダウンロード数', 'citations': '被引用数', 'authorships': 'オーサーシップ数', 'free_instant_usage_percent': 'フリー率%'}
WU_TITLE = L('Weighted Usage (DL + Cit + Auth)', '利用量（加重係数含む）')
STATUS_LABELS = {
    'Show All': L('Show All', 'すべて表示'),
    'TRUE': L('TRUE', 'TRUE（継続）'),
    'FALSE': L('FALSE', 'FALSE（解約）'),
    'MAYBE': L('MAYBE', 'MAYBE（要検討）'),
    '(blank)': L('(blank)', '（空欄・未決定）'),
}
def status_label(x):
    return STATUS_LABELS.get(x, x)

#st.set_page_config(layout="wide")
# ---- Japanese-only explanations: what each graph analyzes ----
EXPLAIN = {
    'usage_cost': """**何を見るか**：ジャーナルごとの「購読費用」と「利用量」の関係です。1つの点が1誌を表します。横軸が購読費用、縦軸が利用量（加重係数含む）で、縦軸は対数目盛です（目盛りが1つ上がるごとに、値がおおよそ10倍になります）。色と形は、購読の値を表します。

**読み方**：同じ費用なら、上にあるジャーナルほど、よく使われていて価値が高いと考えられます。反対に、**右下（高額なのに利用量が少ない）にあるジャーナル**は、費用に見合った利用がされていない可能性があります。

**活用のしかた**：右下にあるジャーナルのうち、まだ購読中（TRUE）のものは、解約を検討する候補になります。右の凡例をクリックすると、その購読の値だけが強調されます。左サイドバーの絞り込みにも連動して、表示が変わります。""",

    'usage_cost_rank': """**何を見るか**：上のグラフと同じ「費用」と「利用量」の関係を、今度は**CPUランク（利用単価の順位）の色**で見るグラフです。形は購読の値のままです。

**読み方**：黄色に近いほどCPUランクが低く（利用単価が安く、効率が良い）、紫の濃い色ほどCPUランクが高い（利用単価が高く、効率が悪い）ことを表します。

**活用のしかた**：右下にあるジャーナルが、実際に濃い色（効率が悪い）になっているかを確認できます。上のグラフで見つけた解約候補が、利用単価の面からも裏付けられるかを、見るために使います。""",

    'authorships': """**何を見るか**：オーサーシップ数（自機関の著者が1人以上いる、そのジャーナルの論文の数。今後5年間の年平均）の、分布です。ジャーナル1誌が1つのブロックで、積み上げて表示されます。色は購読の値です。

**読み方**：多くのジャーナルは、左端（オーサーシップ数が0付近）に集まります。右にいくほど、自機関の研究者が、よく論文を投稿しているジャーナルです。

**活用のしかた**：左サイドバーの「オーサーシップ数の範囲」のスライダーを設定する際の、目安にします。オーサーシップ数が多いジャーナルは、研究者にとって重要度が高い可能性があるため、解約を検討する前に、確認する対象になります。""",

    'dl_cit': """**何を見るか**：ダウンロード数（横軸）と被引用数（縦軸）の関係です。利用量は、ダウンロード数、被引用数、オーサーシップ数から作られるため、そのうち何が利用量を押し上げているかを、分けて見るためのグラフです。

**読み方**：右にあるほどよく読まれ、上にあるほど、自機関の研究で、よく引用されているジャーナルです。**右下**は「よく読まれるが、あまり引用されない」、**左上**は「あまり読まれないが、よく引用される」ジャーナルです。

**活用のしかた**：フィルターでオーサーシップ数をそろえたうえで、そのグループの中で、ダウンロード数と被引用数を比べると、傾向が見やすくなります。""",

    'linked': """**何を見るか**：利用量（縦軸）が、ダウンロード数、被引用数、オーサーシップ数、フリー率（OAまたはPTAで無料入手できる割合）のそれぞれと、どう関係しているかを、4つのグラフで並べたものです。

**読み方**：点が右上がりに並んでいれば、その要素が大きいほど、利用量も大きいことを表します。帯が細く、はっきり右上がりのグラフほど、その要素が利用量をよく説明しています。点が横に広がって上下にばらつくグラフは、その要素と利用量の関係が弱いことを表します。4つのグラフは連動しており、1つをズームすると、全体が連動して変わります。色と形は、購読の値です。

**活用のしかた**：利用量を押し上げている主な要素を、見つけるために使います。フリー率が高いジャーナルは、購読しなくても、無料で読める割合が高いため、購読の必要性が低い可能性があります。""",

    'if_cost': """**何を見るか**：ジャーナルの購読費用（横軸）と、アクセス充足率（IF%、縦軸）の関係です。ここでのIF%は、そのジャーナルが、パッケージ全体のアクセス充足率を、何ポイント分カバーしているか（そのジャーナルの現在の利用 ÷ 全ジャーナルの利用量の合計 × 100）を表します。

**読み方**：上にあるほど、そのジャーナルを購読することで、アクセス充足率が大きく上がります。同じ費用なら、**上にあるジャーナルほど、費用の割に効果が大きい**ことを表します。

**活用のしかた**：同じIF%を得られるなら、より安いジャーナル（同じ高さで左にあるもの）を探せます。**注意**：IF%は、パッケージ内のすべてのジャーナルを合計した値を基準にしているため、一部のジャーナルだけに絞り込むと、計算の基準がずれます。""",

    'if_price': """**何を見るか**：「IF%1ポイントあたりの価格」（横軸、対数目盛）と、アクセス充足率（IF%、縦軸）の関係です。価格で割って、費用対効果をそろえて比べるためのグラフです。

**読み方**：**左上**にあるジャーナルほど、IF%が高く、1ポイントあたりの価格が安い（費用対効果が良い）ことを表します。右にいくほど、少しの充足率の向上のために、大きな費用がかかるジャーナルです。

**活用のしかた**：左上のジャーナルは、購読の維持を検討する候補、右側のジャーナルは、費用対効果の面から、見直しを検討する候補になります。横軸は対数目盛なので、右側が大きく引き伸ばされて見えます。こちらも、全ジャーナルをまとめて見る必要があります。""",

    'cpu_hist': """**何を見るか**：Unsub のヒストグラムを再現したものです。ジャーナルを、利用単価（CPU）の区間ごとに数えて、棒で表します。色は購読の値です。

**読み方**：横軸が左（利用単価が安い）にあるジャーナルほど、効率が良いことを表します。色を見ると、購読している（TRUE）ジャーナルと、解約するとしている（FALSE）ジャーナルが、どの区間に位置しているかが分かります。

**活用のしかた**：購読中のジャーナルが、利用単価の高い側（右）にないかを確認します。また、解約予定のジャーナルが、利用単価の低い側（左）に混じっていないかも、判断の見直しに使えます。Unsub のように、利用単価順に連続して並べるのではなく、購読の値ごとにまとめて表示しています。""",

    'subject': """**何を見るか**：主題分野（subject）ごとに、ジャーナルの CPU ランク（縦軸）を並べたものです。色と形は購読の値です。

**読み方**：縦軸が上にあるほど、CPUランクが高い（効率が悪い）ジャーナルです。分野ごとに、解約するとしている（FALSE）ジャーナルが、どれくらい集まっているかを見ます。

**活用のしかた**：特定の分野だけが、極端に多く解約対象になっていないかを確認し、研究分野への影響が偏らないようにするために使います。主題分野の分類は、完全ではありませんが、おおよその傾向をつかむ目安になります。""",
}

LAYOUT = {
    'usage_cost': "**この表示の構成**：横軸＝購読費用、縦軸＝利用量（加重係数も含む。対数目盛）。1つの点が1誌です。色と形は購読の値を表します（青の十字＝TRUE（継続）、赤の丸＝FALSE（解約）、緑のひし形＝MAYBE（要検討）、灰色の三角＝空欄（未決定））。",
    'usage_cost_rank': "**この表示の構成**：横軸＝購読費用、縦軸＝利用量（対数目盛）。1つの点が1誌です。色＝CPUランク（黄色＝低い・効率が良い、紫＝高い・効率が悪い）、形＝購読の値（十字＝TRUE、丸＝FALSE、ひし形＝MAYBE、三角＝空欄）です。",
    'authorships': "**この表示の構成**：横軸＝オーサーシップ数（今後5年間の年平均）、縦軸＝ジャーナル数です。小さな1ブロックが1誌で、同じ位置のジャーナルは積み上がります。色＝購読の値（青＝TRUE、赤＝FALSE、緑＝MAYBE、灰色＝空欄）です。",
    'dl_cit': "**この表示の構成**：横軸＝ダウンロード数、縦軸＝被引用数。1つの点が1誌です。色と形は購読の値です（十字＝TRUE、丸＝FALSE、ひし形＝MAYBE、三角＝空欄）。",
    'linked': "**この表示の構成**：4つのグラフで、縦軸はすべて利用量（加重係数含む）です。横軸は、左上から順に「ダウンロード数」「被引用数」「オーサーシップ数」「フリー率%」です。1つの点が1誌で、色と形は購読の値を表します。右の凡例をクリックすると、その購読の値だけが強調されます。",
    'if_cost': "**この表示の構成**：横軸＝ジャーナルの費用、縦軸＝アクセス充足率（IF%）。1つの点が1誌です。色と形は購読の値を表します。",
    'if_price': "**この表示の構成**：横軸＝IF%1ポイントあたりの価格（対数目盛。右ほど高い）、縦軸＝アクセス充足率（IF%）。1つの点が1誌です。色と形は購読の値を表します。",
    'cpu_hist': "**この表示の構成**：横軸＝利用単価（CPU）の区間（円では200円刻み、ドルでは1ドル刻み）、縦軸＝ジャーナル数です。小さな1ブロックが1誌で、色は購読の値を表します（青＝TRUE、赤＝FALSE、緑＝MAYBE、灰色＝空欄）。",
    'subject': "**この表示の構成**：横軸＝主題分野、縦軸＝CPUランク（上ほど効率が悪い）です。1つの点が1誌で、色と形は購読の値を表します。",
}

def explain(key):
    # Japanese only
    if lang == '日本語':
        with st.expander('このグラフの見方（分析の内容）', expanded=True):
            st.markdown(LAYOUT[key])
            st.markdown(EXPLAIN[key])

# ---- Japanese names for subject areas (unknown names are shown as-is) ----
SUBJECT_JA = {
    # 'subject' column (Unsub export, May 2022+)
    'Agricultural and Biological Sciences': '農学・生物科学',
    'Chemistry and Chemical Engineering': '化学・化学工学',
    'Computer Science': 'コンピュータサイエンス',
    'Earth and Planetary Sciences': '地球惑星科学',
    'Economics, Business and Management': '経済学・経営学',
    'Engineering, Energy and Technology': '工学・エネルギー・技術',
    'Environmental Sciences': '環境科学',
    'Life Sciences': '生命科学',
    'Materials Science': '材料科学',
    'Mathematics': '数学',
    'Medicine': '医学',
    'Neuroscience': '神経科学',
    'Nursing': '看護学',
    'Pharmacology, Pharmaceutical Science and Toxicology': '薬理学・薬学・毒性学',
    'Physics and Astronomy': '物理学・天文学',
    'Social and Behavioral Sciences': '社会・行動科学',
    'Veterinary Science and Veterinary Medicine': '獣医学',
    'Arts and Humanities': '芸術・人文学',
    'Dentistry': '歯学',
    'Health Professions': '医療専門職',
    'Immunology and Microbiology': '免疫学・微生物学',
    'Psychology': '心理学',
    'Social Sciences': '社会科学',
    'Multidisciplinary': '学際',
    # MAG/OpenAlex-style field names (Unsub 'subject' column)
    'Art': '芸術',
    'Biology': '生物学',
    'Business': '経営学',
    'Chemistry': '化学',
    'Computer science': 'コンピュータサイエンス',
    'Environmental science': '環境科学',
    'Geography': '地理学',
    'Geology': '地質学',
    'History': '歴史学',
    'Materials science': '材料科学',
    'Philosophy': '哲学',
    'Physics': '物理学',
    'Political science': '政治学',
    'Sociology': '社会学',
    'Law': '法学',
    'Linguistics': '言語学',
    'Psychology': '心理学',
    '0': '分類なし',
    'nan': '分類なし',
    # old 'era_subjects' column (ERA two-digit fields)
    'Mathematical Sciences': '数理科学',
    'Physical Sciences': '物理科学',
    'Chemical Sciences': '化学',
    'Earth Sciences': '地球科学',
    'Biological Sciences': '生物科学',
    'Agricultural and Veterinary Sciences': '農学・獣医学',
    'Information and Computing Sciences': '情報・計算機科学',
    'Engineering': '工学',
    'Technology': '技術',
    'Medical and Health Sciences': '医学・健康科学',
    'Built Environment and Design': '建築環境・デザイン',
    'Education': '教育学',
    'Economics': '経済学',
    'Commerce, Management, Tourism and Services': '商学・経営学・観光・サービス',
    'Studies in Human Society': '人間社会研究',
    'Psychology and Cognitive Sciences': '心理学・認知科学',
    'Law and Legal Studies': '法学・法律研究',
    'Studies in Creative Arts and Writing': '創造芸術・文筆研究',
    'Language, Communication and Culture': '言語・コミュニケーション・文化',
    'History and Archaeology': '歴史学・考古学',
    'Philosophy and Religious Studies': '哲学・宗教学',
}

SUBJECT_JA_LC = {k.strip().lower(): t for k, t in SUBJECT_JA.items()}

def subject_label(v):
    if lang == '日本語':
        _k = str(v).strip()
        return SUBJECT_JA.get(_k, SUBJECT_JA_LC.get(_k.lower(), v))
    return v


# ---- Help texts for the sidebar filters ----
FILTER_HELP = {
    'price': ('Keeps only journals whose subscription cost is inside this range. Raising the lower end hides cheap journals; lowering the upper end hides expensive ones.',
              '購読費用がこの範囲に入るジャーナルだけを表示します。下限を上げると安いジャーナルが、上限を下げると高額なジャーナルが、グラフと集計から消えます。例：上限を下げると「高額誌を除いた状況」を見られ、下限を上げると「高額誌だけ」を見られます。'),
    'cpu': ('CPU rank 1 = most cost-efficient. Restricting to the high end shows the least efficient journals.',
            'CPUランクは 1 が最も効率が良く、数字が大きいほど効率が悪くなります。範囲の下限を上げて「上位（数字の大きい側）」に絞ると、利用単価が高い＝見直し候補のジャーナルだけが残ります。逆に上限を下げると、効率の良いジャーナルだけが残ります。'),
    'downloads': ('Annual average downloads over the next five years. Restricting to the high end shows heavily read journals.',
                  'ダウンロード数（今後5年間の年平均）の範囲です。下限を上げると、よく読まれているジャーナルだけが残り、上限を下げると、あまり読まれていないジャーナルだけが残ります。'),
    'citations': ('Annual average citations by your institution\'s authors over the next five years.',
                  '被引用数（今後5年間の年平均）の範囲です。自機関の研究で、よく引用されているジャーナルを探すときは、下限を上げます。'),
    'authorships': ('Annual average number of papers with at least one author from your institution.',
                    'オーサーシップ数（自機関の著者が含まれる論文の数。今後5年間の年平均）の範囲です。下限を上げると、自機関の研究者がよく投稿しているジャーナルだけが残ります。解約を検討する前に、このスライダーで「研究者にとって重要なジャーナル」を確認できます。'),
    'usage': ('Weighted usage = downloads + x*citations + y*authorships. Restricting hides little-used or heavily used journals.',
              '利用量＝ダウンロード数 + x×被引用数 + y×オーサーシップ数（加重係数 x、y は Unsub 側で設定）の範囲です。上限を下げると利用の少ないジャーナルだけが、下限を上げるとよく使われるジャーナルだけが残ります。'),
    'free': ('Share of use available free via OA or PTA. A high value means the journal can mostly be read without a subscription.',
             'フリー率（OA または PTA で無料入手できる利用の割合）の範囲です。下限を上げると、購読しなくても読める割合が高いジャーナルだけが残り、解約しても影響が小さい候補を探せます。上限を下げると、購読しないと読めないジャーナルだけが残ります。'),
    'oa': ('Share of use available as Open Access.',
           'OA率（オープンアクセスで読める利用の割合）の範囲です。下限を上げると、OA で読める割合が高いジャーナルだけが残ります。'),
    'subscribed': ('Show only journals with the selected Subscribed value.',
                   '現在の「購読」の値で絞り込みます。「すべて表示」以外を選ぶと、その値のジャーナルだけを表示します（TRUE=購読継続、FALSE=解約、MAYBE=要検討、空欄=未決定）。'),
}

def FH(key):
    return L(*FILTER_HELP[key])

# ---- Visible explanation under each filter (static caption + live count) ----
FILTER_DESC = {
    'price': ('Subscription cost. Raising the lower end leaves only expensive journals; lowering the upper end leaves only cheap ones.',
              '購読費用で絞ります。\n- 下限を上げる → 高額なジャーナルだけが残ります（解約すると大きく節約できる候補を探すとき）。\n- 上限を下げる → 高額なジャーナルが消え、安価なものだけが残ります。'),
    'cpu': ('CPU rank (1 = most cost-efficient).',
            'CPUランク（1が最も効率が良く、数字が大きいほど効率が悪い）で絞ります。\n- 下限を上げる → 効率の悪い（利用単価が高い）ジャーナルだけが残ります。解約候補の確認に使います。\n- 上限を下げる → 効率の良いジャーナルだけが残ります。'),
    'downloads': ('Downloads (annual average, next 5 years).',
                  'ダウンロード数（今後5年間の年平均）で絞ります。\n- 下限を上げる → よく読まれているジャーナルだけが残ります。\n- 上限を下げる → あまり読まれていないジャーナルだけが残ります（利用の少ない解約候補を探すとき）。'),
    'citations': ('Citations (annual average, next 5 years).',
                  '被引用数（自機関の論文からの引用。今後5年間の年平均）で絞ります。\n- 下限を上げる → 自機関の研究でよく引用されているジャーナルだけが残ります。\n- 上限を下げる → ほとんど引用されていないジャーナルだけが残ります。'),
    'authorships': ('Authorships (annual average, next 5 years).',
                    'オーサーシップ数（自機関の著者を含む論文の数。今後5年間の年平均）で絞ります。\n- 下限を上げる → 自機関の研究者がよく投稿しているジャーナルだけが残ります（解約の影響が大きいものの確認）。\n- 上限を下げる → 自機関からの投稿が少ないジャーナルだけが残ります。'),
    'usage': ('Weighted usage = downloads + x*citations + y*authorships.',
              '利用量（ダウンロード + x×被引用 + y×オーサーシップ）で絞ります。\n- 下限を上げる → 総合的によく使われているジャーナルだけが残ります。\n- 上限を下げる → 利用の少ないジャーナルだけが残ります。'),
    'free': ('Free % = share of use available via OA or PTA.',
             'フリー率（OAまたはPTAで無料入手できる利用の割合）で絞ります。\n- 下限を上げる → 購読しなくても読める割合が高いジャーナルだけが残ります。解約しても影響が小さい候補を探せます。\n- 上限を下げる → 購読しないと読めないジャーナルだけが残ります。'),
    'oa': ('OA % = share of use available as Open Access.',
           'OA率（オープンアクセスで読める利用の割合）で絞ります。\n- 下限を上げる → OAで読める割合が高いジャーナルだけが残ります。\n- 上限を下げる → OAで読める割合が低いジャーナルだけが残ります。'),
    'subscribed': ('Show only journals with the selected Subscribed value.',
                   '購読の値で絞ります。\n- 「すべて表示」以外を選ぶと、その値のジャーナルだけを表示します。\n- TRUE=購読継続、FALSE=解約、MAYBE=要検討、空欄=未決定。'),
}

def FD(key):
    """Show the explanation under a filter and return a slot for the live count."""
    st.sidebar.caption(L(*FILTER_DESC[key]))
    return st.sidebar.empty()

def filter_note():
    st.sidebar.caption(L('Filters only change what is displayed; your CSV and Subscribed values are not changed. All conditions are combined with AND.',
                         '絞り込みは表示を変えるだけで、CSVや購読の値は変わりません。すべての条件は「かつ（AND）」で組み合わさります。'))
st.image('unsub_extender2.png')
st.markdown(L("##### :books: Paper on Unsub Extender published in [*Quantitative Science Studies*](https://doi.org/10.1162/qss_a_00200)",
              "##### :books: Unsub Extender に関する論文が [*Quantitative Science Studies*](https://doi.org/10.1162/qss_a_00200) に掲載されています（英語）"))
#st.markdown("##### :tada: Recipient of the 2022 RUSA ETS [Best Emerging Technology Application](https://rusaupdate.org/2022/03/2022-ets-best-emerging-technology-application-award/) Award")
#st.markdown("##### and the 2022 ASEE ELD [Innovation in Access to Engineering Information](https://sites.asee.org/eld/about-the-eld/awards/#innovation) Award :tada:")



with st.expander(L("How to use:", "使い方:")):
    st.write(L(":wave: Learn more about using Unsub Extender by watching a [live demo](https://vimeo.com/680578098)",
               ":wave: 使い方は[ライブデモ動画](https://vimeo.com/680578098)（英語）でも紹介されています"))
    st.write(L("Unsub is a tool that analyzes academic journal subscriptions to help libraries better understand their value. However, Unsub does not make it easy to understand all the complex and interrelated data it provides.",
               "Unsub は、学術ジャーナルの購読の価値を図書館が把握しやすくするための分析ツールです。ただし、Unsub が提供する複雑で相互に関連したデータ全体を読み解くのは簡単ではありません。"))
    st.write(L("**Unsub Extender** takes an Unsub data export .csv file and automates the creation of useful plots and interactive visualizations so you can make more informed collection decisions.",
               "**Unsub Extender** は、Unsub からエクスポートした .csv ファイルを読み込み、有用なグラフやインタラクティブな可視化を自動で作成します。蔵書（コレクション）に関する判断の材料としてご利用ください。"))
    st.write(L('**Upload your specific Unsub .csv** export file using the "Browse files" button in the left sidebar, or explore the pre-loaded example dataset and plots to see what is available.',
               '左サイドバーの「Browse files」ボタンから、**お手持ちの Unsub のエクスポート .csv ファイルをアップロード**してください。アップロードしない場合は、あらかじめ読み込まれているサンプルデータで機能を試せます。'))
    st.write(L("Graphs are interactive and support zoom, click-and-drag, and hover.  Double click a graph to reset back to the default view.",
               "グラフはズーム、クリック＆ドラッグ、ホバー（マウスオーバー）に対応しています。グラフをダブルクリックすると初期表示に戻ります。"))
    st.write(L("Filter on various criteria using the sliders on the left to narrow in on areas of interest, hover over data points to learn more about a specific journal, then use the dropdown to actually change a journal's *Subscribed* status and watch the graphs update. (Note: you may have to occasionally hit *'r'* to force a reload if you notice it's not loading right away)",
               "左のスライダーでさまざまな条件による絞り込みを行い、気になる範囲を探します。データ点にマウスを重ねるとそのジャーナルの詳細が表示されます。ドロップダウンでジャーナルの *購読*を変更すると、グラフに反映されます。（注：うまく読み込まれないときは、キーボードの *'r'* を押して再読み込みしてください）"))
    st.write(L("Note: Subscribed values are TRUE (keep), FALSE (cancel), MAYBE (think more) and blank (no decision yet). The values themselves are always kept in English so that the exported .csv stays compatible with Unsub.",
               "補足：購読の値は、TRUE（継続）、FALSE（解約）、MAYBE（要検討）、空欄（未決定）です。ダウンロードする .csv を Unsub と互換に保つため、値そのものは日本語表示でも英語のままです。"))
    st.markdown(L('This project is written in Python and deployed as a web app using the library Streamlit.',
                  'このプロジェクトは Python で書かれ、Streamlit ライブラリで Web アプリとして動作します。'))
    st.markdown(L('**More information about Unsub Extender, its requirements, and the source code is available on the [project GitHub page](https://github.com/eschares/unsub_extender)**',
                  '**Unsub Extender の詳細、必要なファイル形式、ソースコードは[元プロジェクトの GitHub ページ](https://github.com/eschares/unsub_extender)をご覧ください**（英語）'))
    st.markdown(L('This is an unofficial Japanese-localized version (modified from the original, AGPL-3.0).',
                  'このアプリは、元プロジェクト（Eric Schares 作、AGPL-3.0）を改変した、非公式の日本語対応版です。'))

with st.expander(L("How the numbers are calculated", "計算のしくみ")):
    st.markdown(L(
"""**Most numbers come straight from Unsub. This app calculates only a few itself.**

##### 1. Values calculated by Unsub (shown as-is)
- **Weighted usage (usage)**: Downloads + x × Citations + y × Authorships. The weights x and y are set in Unsub.
- **CPU (cost per use)**: Unsub's refined cost per use = (subscription cost − ILL cost) ÷ weighted usage that is *not* available for free (OA or PTA). Lower is more cost-efficient. It can even be negative when the estimated ILL cost exceeds the subscription cost.
- **CPU rank**: CPU turned into a rank. Higher numbers are less cost-efficient (the highest CPU gets the highest rank number, equal to the number of journals).
- **Free %**: the share of use that can be fulfilled via Open Access or PTA (post-termination access rights).

So CPU is not simply cost ÷ weighted usage. (Source: Unsub documentation, "Cost per use (CPU)" and "Data export".)

##### 2. Values calculated by this app
**Instant Fill % (IF%)** shows how much of the whole package's use a journal covers as "available right away".

1. Current usage of a journal = (subscription % + ILL % + unknown %) ÷ 100 × weighted usage
2. IF% = current usage of the journal ÷ total weighted usage of all journals × 100
3. Price per 1 IF% point = subscription cost ÷ IF%

*Example (Journlia in the sample data)*: ILL 0% and unknown 4%, weighted usage 722, so current usage is about 722 × 4% = 28.9. The total over all journals is about 399,000, so IF% is about 0.007%. With a cost of 8,273 USD, the price per 1 IF% point is about 1.14 million USD. The smaller this price is, the cheaper a journal covers use (upper left in the graph).

**Caveats**
- The `instant_usage_percent` column in the Unsub export is the share of one journal's own usage that is available instantly. The IF% here is each journal's contribution (in points) to the package-wide Instant Fill / access fulfillment rate, so the two values are not the same.
- The total in step 2 always uses all journals, not the filtered ones.
- The app assumes the subscription % is 0 for every journal (i.e. no subscription yet).
- Journals with weighted usage of 0 are set to 1 so the log-scale graphs can be drawn.

##### 3. Other totals
- "rows selected" at the top: the number of journals left after filtering, and the total subscription cost of them.
- The small table: count and total cost for each Subscribed value (TRUE / FALSE / MAYBE / blank).

##### 4. How to read the graphs
- In "Weighted Usage vs. Cost", journals toward the lower right (expensive but little used) are candidates for cancellation.
- For the CPU rank, smaller is better and larger is a candidate for review.
- Use the Instant Fill % graphs to look for "the same coverage at a lower price".
""",
"""**ほとんどの数値は、Unsub が計算した値をそのまま使っています。このアプリ自身が計算するのは、ごく一部です。**

##### 1. Unsub が計算済みの値（そのまま表示）
- **利用量（usage、加重係数含む）**：ダウンロード数 + x × 被引用数 + y × オーサーシップ数。加重係数 x、y は、Unsub 側で設定した値です。
- **CPU（利用単価）**：Unsub 独自の利用単価で、（購読費用 − ILL 費用）÷「無料（OA または PTA）で入手できる分を除いた利用量」です。小さいほどコスト効率が良いことを表します。ILL 費用の見込みが購読費用を上回ると、マイナスになることもあります。
- **CPUランク**：CPU を順位にしたもの。数字が大きいほど効率が悪くなります（CPU が最も高いジャーナルが最大値で、ジャーナル数と同じになります）。
- **フリー率**：利用のうち、オープンアクセス（OA）または PTA（契約終了後のアクセス権）で満たせる割合です。

このため CPU は、単純な「費用 ÷ 利用量」ではありません。（出典：Unsub ドキュメントの「Cost per use (CPU)」「Data export」）

##### 2. このアプリが計算する値
**アクセス充足率（Instant Fill, IF%）** は、Unsub の画面で「アクセス充足率」として表示される、パッケージ全体の利用のうち「すぐに入手できる割合」です。このアプリでは、**各ジャーナルがその全体の率を何ポイント分カバーしているか**を計算します。

1. ジャーナルごとの現在の利用 ＝（購読% + ILL% + 不明（その他の経路）%）÷ 100 × 利用量
2. IF% ＝ そのジャーナルの現在の利用 ÷ 全ジャーナルの利用量の合計 × 100
3. IF%1ポイントあたりの価格 ＝ 購読費用 ÷ IF%

*計算例（サンプルデータの Journlia）*：ILL 0%、不明（その他の経路） 4%、利用量 722 なので、現在の利用は 722 × 4% ＝ 約 28.9 です。全ジャーナルの合計は約 39.9万なので、IF% は約 0.007% になります。費用が 8,273 ドルなので、IF%1ポイントあたりの価格は約 114万ドルです。この価格が小さいほど、安くカバーしているジャーナルです（グラフでは左上）。

**注意点**
- Unsub の書き出しファイルの `instant_usage_percent` 列は、そのジャーナル単体の利用のうち、すぐに入手できる割合です。このアプリの IF% は、それを全体に対する寄与（ポイント）として計算し直したもので、同じ値ではありません。
- 手順2の合計は、絞り込み後ではなく、常に全ジャーナルを対象にします。
- 購読% はすべてのジャーナルで 0（まだ契約していない状態）とみなして計算します。
- 利用量が 0 のジャーナルは、対数グラフを描くため 1 に置き換えます。

##### 3. そのほかの集計
- 画面上部の「○行を選択」：絞り込み後のジャーナル数と、その購読費用の合計です。
- 小さな表：購読の値（TRUE / FALSE / MAYBE / 空欄）ごとの、件数と費用の合計です。

##### 4. グラフの読み方
- 「利用量 vs. コスト」では、右下（高額なのに利用が少ない）のジャーナルが、解約を検討する候補です。
- CPUランクは、小さいほど良く、大きいほど見直しの候補です。
- アクセス充足率のグラフでは、「同じカバー率なら、より安いもの」を探します。
"""))

# Limit tick-label width so that extreme zoom levels do not push titles out of the page
def _ue_theme():
    return {'config': {'axisY': {'labelLimit': 70}, 'axis': {'titleLimit': 400}, 'autosize': {'type': 'fit', 'contains': 'padding'}}}
alt.themes.register('ue_theme', _ue_theme)
alt.themes.enable('ue_theme')

#==== Load Data ====
#Initialize with a hardcoded dataset
file = filename = "Unsub_export_example.csv"

st.sidebar.subheader(L('Upload your Unsub export file', 'Unsub のエクスポートファイルをアップロード'))
uploaded_file = st.sidebar.file_uploader(L("Must be a .csv file", ".csv ファイルを選択してください"), type='csv')
st.sidebar.caption(L('The uploaded file is processed on the server that runs this app.', 'アップロードしたファイルは、このアプリを動かしているサーバーで処理されます。'))
if uploaded_file is not None:
    file_details = {"FileName":uploaded_file.name,"FileType":uploaded_file.type,"FileSize":uploaded_file.size}
    #st.write(file_details)
    
    file = uploaded_file
    filename = uploaded_file.name

# ---- Currency switch (Yen / USD) ----
currency = st.sidebar.radio(L('Currency of the amounts in your file', 'ファイルの金額の通貨'), ['JPY', 'USD'],
                            format_func=lambda x: L('Yen (¥)', '円（¥）') if x == 'JPY' else '$ (USD)',
                            index=0 if uploaded_file is not None else 1,
                            help=L('No exchange-rate conversion is done. Choose the currency the amounts in your Unsub export are already in. The bundled sample data is in USD.', '為替の換算はしません。Unsub のエクスポートの金額が、すでに円なら「円」、ドルなら「$」を選んでください。付属のサンプルデータはドル建てです。'),
                            key=('currency_upload' if uploaded_file is not None else 'currency_sample'))   # separate keys: the sample (USD) must not inherit a yen choice made for an uploaded file
st.sidebar.caption(L('Amounts are shown as they are in the file. No exchange-rate conversion is done.', '金額はファイルの値のまま表示します。為替の換算はしません。'))
IS_JPY = (currency == 'JPY')
CUR = '¥' if IS_JPY else '$'

def money(x):
    return CUR + "{:,.0f}".format(x)

def money_axis(spec=',.2r', usd='$,.2r'):
    # Axis with currency symbol. d3 format '$' is USD only, so yen uses labelExpr.
    if IS_JPY:
        return alt.Axis(format=spec, labelExpr="'¥' + format(datum.value, '" + spec + "')")
    return alt.Axis(format=usd)

# CPU histogram: bin width / initial x range (yen: about 16,000 yen, USD: 100 dollars)
HIST_STEP = 200 if IS_JPY else 1
HIST_DOMAIN = [-200, 16000] if IS_JPY else [-1, 100]
HIST_MAX_EN = '¥16,000' if IS_JPY else '$100'
HIST_MAX_JA = '16,000円' if IS_JPY else '$100'

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def load_data(file):
    st.write(L("New file loaded", "新しいファイルを読み込みました"))
    # Some exports have extra title rows (e.g. 'export (1)') above the header line; look for the real header row
    for skip in range(0, 6):
        if hasattr(file, 'seek'):
            file.seek(0)
        df_try = pd.read_csv(file, skiprows=skip)
        if 'subscribed' in df_try.columns and 'title' in df_try.columns:
            return df_try
    if hasattr(file, 'seek'):
        file.seek(0)
    return pd.read_csv(file)

st.header(L('Analyzing file "' + filename + '"', 'ファイル「' + filename + '」を分析中'))

# .copy(): the cached DataFrame is shared by all sessions; work on a private copy so one user's edits never reach another user
df = load_data(file).copy()

_required_cols = ['title', 'downloads', 'citations', 'authorships', 'usage', 'subscription_cost', 'subscribed', 'cpu', 'cpu_rank',
                  'use_ill_percent', 'use_oa_percent', 'use_other_delayed_percent', 'use_subscription_percent', 'free_instant_usage_percent']
_missing_cols = [c for c in _required_cols if c not in df.columns]
if _missing_cols:
    st.error(L("The file is missing required columns: ", "必要な列がファイルにありません: ") + ", ".join(_missing_cols))
    st.write(L("Please upload the .csv file exported from an Unsub scenario (Export - Download as spreadsheet).",
               "Unsub のシナリオから書き出した .csv（「エクスポート」→「スプレッドシートとしてダウンロード」）をアップロードしてください。"))
    st.stop()



#==== Pre-process data ====
#force 'subscribed' column to be a string, not Bool and all uppercase
df['subscribed'] = df['subscribed'].fillna(' ')     #blank Subscribed values turn into a space
df['subscribed'] = df['subscribed'].astype(str)
df['subscribed'] = df['subscribed'].str.upper()
if ('perpetual_access_years' in df.columns):
    df['perpetual_access_years'] = df['perpetual_access_years'].astype(str)
if ('perpetual_access_years_text' in df.columns):
    df['perpetual_access_years_text'] = df['perpetual_access_years_text'].astype(str)

#convert subject and era_subjects columns to strings, sometimes they are left blank and get coverted to 0/ints which screws everything up
if ('subject' in df.columns):
    df['subject'] = df['subject'].astype(str)
if ('era_subjects' in df.columns):
    df['era_subjects'] = df['era_subjects'].astype(str)
if ('subject_top_three' in df.columns):
    df['subject_top_three'] = df['subject_top_three'].astype(str)
if ('subjects_all' in df.columns):
    df['subjects_all'] = df['subjects_all'].astype(str)
if ('Notes' in df.columns):
    df['Notes'] = df['Notes'].astype(str)
if ('publisher' in df.columns):
    df['publisher'] = df['publisher'].astype(str)
for fuzzed_col in df.loc[:,df.columns.str.endswith('fuzzed')]:
    df[fuzzed_col] = df[fuzzed_col].astype(str)


#handle cases where a '-' is in the cell, seems to happen in cpu and cpu_rank
df['cpu'] = pd.to_numeric(df['cpu'], errors='coerce')
df['cpu_rank'] = pd.to_numeric(df['cpu_rank'], errors='coerce')     #changes '-' to not a number
df = df.replace(np.nan, 0, regex=True)  #changes that to 0
df['cpu_rank'] = df['cpu_rank'].astype(int)
fix_filt = (df['cpu_rank']==0)
df.loc[fix_filt,'cpu_rank']= int(max(df['cpu_rank']))   #moves cpu_rank of 0 to max cpu_rank number

#move anything with weighted usage of 0 to 1 so log graphs work
df = df.replace({'usage':0}, 1)

#process data to calculate IF%
#check and don't redo if IF% column already exists - rerunning a file through UE
if not 'IF%' in df.columns:
    total_usage = df['usage'].sum()
    df['current_yr_usage'] = ((df['use_subscription_percent'] + df['use_ill_percent'] + df['use_other_delayed_percent']) / 100) * df['usage']  #assumes subscription comes in as 0 everywhere, set to FALSE
    df['IF%'] = (df['current_yr_usage'] / total_usage) * 100
    df['cost_per_IF%'] = df['subscription_cost'] / df['IF%']

st.sidebar.subheader(L("Change a journal's Subscribed status", "ジャーナルの購読を変更"))
sidebar_modifier_slot = st.sidebar.empty()
my_slot1 = st.empty()   #save this spot to fill in later for how many rows get selected with the filter


if max(df['citations']) == 0:
          1 #set a random cell to 0.1
if max(df['authorships']) == 0:
          1 #set a random cell to 0.1

# Sliders and filter
st.sidebar.subheader(L("**Filters** (arrow keys to fine-tune)", "**絞り込み**（矢印キーで微調整できます）"))
filter_note()
price_slider = st.sidebar.slider(L('Price (' + CUR + ') between:', '価格 (' + CUR + ') の範囲:'), min_value=0, max_value=int(max(df['subscription_cost'])), value=(0,int(max(df['subscription_cost']))))
_slot_price = FD('price')
cpu_slider = st.sidebar.slider(L('Cost per Use Rank between:', 'CPU（利用単価）ランクの範囲:'), min_value=int(min(df['cpu_rank'])), max_value=int(max(df['cpu_rank'])), value=(int(min(df['cpu_rank'])),int(max(df['cpu_rank']))))
_slot_cpu = FD('cpu')
downloads_slider = st.sidebar.slider(L('Downloads between:', 'ダウンロード数の範囲:'), min_value=0, max_value=int(max(df['downloads'])), value=(0,int(max(df['downloads']))))
_slot_downloads = FD('downloads')
citations_slider = st.sidebar.slider(L('Citations between:', '被引用数の範囲:'), min_value=0.0, max_value=max(df['citations']), value=(0.0,max(df['citations'])))
_slot_citations = FD('citations')
authorships_slider = st.sidebar.slider(L('Authorships between:', 'オーサーシップ数の範囲:'), min_value=0.0, max_value=max(df['authorships']), value=(0.0,max(df['authorships'])))
_slot_authorships = FD('authorships')
weighted_usage_slider = st.sidebar.slider(L('Weighted usage (DL + x*Cit + y*Auth) between:', '利用量（加重係数含む）の範囲:'), min_value=0, max_value=int(max(df['usage'])), value=(0,int(max(df['usage']))))
_slot_usage = FD('usage')
free_percent_slider = st.sidebar.slider(L('Free % (OA + backfile) between:', 'フリー率 % (OA + PTA) の範囲:'), min_value=0, max_value=int(max(df['free_instant_usage_percent'])), value=(0,int(max(df['free_instant_usage_percent']))))
_slot_free = FD('free')
OA_percent_slider = st.sidebar.slider(L('OA % between:', 'OA率 % の範囲:'), min_value=0, max_value=int(max(df['use_oa_percent'])), value=(0,int(max(df['use_oa_percent']))))
_slot_oa = FD('oa')
subscribed_filter = st.sidebar.radio(L('Subscribed status:', '購読:'), ['Show All', 'TRUE', 'FALSE', 'MAYBE', '(blank)'],
                                     format_func=status_label,
                                     help=L('Filter based on the current Subscribed status', '現在の購読の値で絞り込みます'))
_slot_subscribed = FD('subscribed')
subscribed_filter_flag = 0
if subscribed_filter == "(blank)":
    subscribed_filter = " "
if subscribed_filter != 'Show All':
    subscribed_filter_flag = 1

#could also use between: (df['cpu_rank'].between(cpu_slider[0], cpu_slider[1]))
filt = ( (df['use_oa_percent'] >= OA_percent_slider[0]) & (df['use_oa_percent'] <= OA_percent_slider[1]) &
        (df['free_instant_usage_percent'] >= free_percent_slider[0]) & (df['free_instant_usage_percent'] <= free_percent_slider[1]) &
        (df['downloads'] >= downloads_slider[0]) & (df['downloads'] <= downloads_slider[1]) &
        (df['citations'] >= citations_slider[0]) & (df['citations'] <= citations_slider[1]) &
        (df['subscription_cost'] >= price_slider[0]) & (df['subscription_cost'] <= price_slider[1]+1) &     #subtle bug where most expensive journal doesn't show if price has cents b/c $100.10 is greater than int($100)
        (df['authorships'] >= authorships_slider[0]) & (df['authorships'] <= authorships_slider[1]) &
        (df['cpu_rank'] >= cpu_slider[0]) & (df['cpu_rank'] <= cpu_slider[1]) &
        (df['usage'] >= weighted_usage_slider[0]) & (df['usage'] <= weighted_usage_slider[1])
        )

if subscribed_filter_flag:  # add another filter part, have to do it this way so Subscribed=ALL works
    filt2 = (df['subscribed'] == subscribed_filter)
    filt = filt & filt2



# if st.checkbox('Show raw data'):
#     st.subheader('Raw data')
#     st.write(df[filt])
    
my_slot2 = st.empty()   #save this spot to fill in later with the summary table of counts and sum$ by Subscribed

#Report the number of journals the filter selected
# live count under each filter: how many journals fit that one condition
_n_all = len(df)
def _cnt(col, rng, pad=0):
    return int(((df[col] >= rng[0]) & (df[col] <= rng[1] + pad)).sum())
_live_msg = lambda n: L("→ %d of %d journals fit this condition" % (n, _n_all), "→ この条件に合うジャーナル：%d / %d 誌" % (n, _n_all))
_slot_price.caption(_live_msg(_cnt('subscription_cost', price_slider, 1)))
_slot_cpu.caption(_live_msg(_cnt('cpu_rank', cpu_slider)))
_slot_downloads.caption(_live_msg(_cnt('downloads', downloads_slider)))
_slot_citations.caption(_live_msg(_cnt('citations', citations_slider)))
_slot_authorships.caption(_live_msg(_cnt('authorships', authorships_slider)))
_slot_usage.caption(_live_msg(_cnt('usage', weighted_usage_slider)))
_slot_free.caption(_live_msg(_cnt('free_instant_usage_percent', free_percent_slider)))
_slot_oa.caption(_live_msg(_cnt('use_oa_percent', OA_percent_slider)))
_slot_subscribed.caption(_live_msg(_n_all if not subscribed_filter_flag else int((df['subscribed'] == subscribed_filter).sum())))
selected_jnls = str(df[filt].shape[0])
total_jnls = str(df.shape[0])
cost_sum = df[filt]['subscription_cost'].sum()  #cost of selected journals
currency_string = money(cost_sum)   #format with $, commas, and no decimal points
my_slot1.subheader(L(selected_jnls + ' rows selected out of ' + total_jnls + ' rows, costing a total of ' + currency_string,
                      total_jnls + ' 行中 ' + selected_jnls + ' 行を選択（合計費用: ' + currency_string + '）'))


#set up the color maps on 'subscribed'
subscribed_colorscale = alt.Scale(domain = ['TRUE', 'FALSE', 'MAYBE', ' '],
                                  range = ['blue', 'red', 'green', 'gray'])

subscribed_point_mapping = alt.Scale(domain=['TRUE', 'FALSE', 'MAYBE', ' '],
                                     range=["cross", "circle", "diamond", "triangle-up"]    #The scale property allow you to map a domain to a range, where the domain specifies input values, and the range specifies the visual properties to which the domain is mapped. If you want multiple domain values to map to the same range value, it can be done like this:
                                         )

# Function to remove a title from all four lists in preparation for adding back to one list
def clear_title_from_list(title):
    if title in st.session_state.to_true:
        st.session_state.to_true.remove(title)
        st.write(L('Removed ', ''), title, L("from st.to_true list", "を st.to_true リストから削除しました"))
    
    if title in st.session_state.to_false:
        st.session_state.to_false.remove(title)
        st.write(L('Removed ', ''), title, L("from st.to_false list", "を st.to_false リストから削除しました"))
        
    if title in st.session_state.to_maybe:
        st.session_state.to_maybe.remove(title)
        st.write(L('Removed ', ''), title, L("from st.to_maybe list", "を st.to_maybe リストから削除しました"))
        
    if title in st.session_state.to_blank:
        st.session_state.to_blank.remove(title)
        st.write(L('Removed ', ''), title, L("from st.to_blank list", "を st.to_blank リストから削除しました"))

# Initialize session_state versions of to_true/false/maybe/blank lists
if 'to_true' not in st.session_state:
    st.session_state.to_true = []
if 'to_false' not in st.session_state:
    st.session_state.to_false = []
if 'to_maybe' not in st.session_state:
    st.session_state.to_maybe = []
if 'to_blank' not in st.session_state:
    st.session_state.to_blank = []


#Put Modifier down here after the filt definition so only those titles that meet the filt show up, but put into empty slot further up the sidebar for flow
with sidebar_modifier_slot:
    with st.expander(L("Expand to select:", "開いて選択:")):
        filtered_titles_df = df.loc[filt]['title']      #make a new df with only the valid titles
        #then give those valid titles as choices in the Modifier, was causing problems when trying to offer them through a filter, kept trying to use the index but wouldn't be there anymore
        selected_titles = st.multiselect(L('Journal Name:', 'ジャーナル名:'), pd.Series(filtered_titles_df.reset_index(drop=True)), help=L('Displayed in order provided by the underlying datafile', 'ファイル内の並び順で表示されます'))
        #st.write(selected_titles)
    
        col1, col2 = st.columns([2,1])
    
        with col1:
            radiovalue = st.radio(L("Change 'Subscribed' status to:", "「購読」を次の値に変更:"), ['TRUE', 'MAYBE', 'FALSE', '(blank)'], format_func=status_label)
            if radiovalue == "(blank)":
                radiovalue = " "
                #write(radiovalue)
        with col2:
            st.write(" ")       #Move the Commit button down vertically
            st.write(" ")       #I'm sure there's a smarter way to do this, but oh well
            if st.button(L('Commit change!', '変更を確定！')):
                for title in selected_titles:
                    clear_title_from_list(title)  #remove title from all lists, so we only keep the most recent change
                                                    #note we are not clearing all 4 lists, just removing one title at a time

                if radiovalue == 'TRUE':
                    for title in selected_titles:
                        st.session_state.to_true.append(title)
                        
                if radiovalue == 'FALSE':
                    for title in selected_titles:
                        st.session_state.to_false.append(title)
                        
                if radiovalue == 'MAYBE':
                    for title in selected_titles:
                        st.session_state.to_maybe.append(title)
                        
                if radiovalue == " ":
                    for title in selected_titles:
                        st.session_state.to_blank.append(title)


# Actually do the changes in df; this runs every time the script runs but session_state lets me save the previous changes
for title in st.session_state.to_true:
    title_filter = (df['title'] == title)
    df.loc[title_filter, 'subscribed'] = 'TRUE'

for title in st.session_state.to_false:
    title_filter = (df['title'] == title)
    df.loc[title_filter, 'subscribed'] = 'FALSE'
    
for title in st.session_state.to_maybe:
    title_filter = (df['title'] == title)
    df.loc[title_filter, 'subscribed'] = 'MAYBE'
    
for title in st.session_state.to_blank:
    title_filter = (df['title'] == title)
    df.loc[title_filter, 'subscribed'] = ' '





if st.checkbox(L('Show raw data', '元データを表示')):
    st.subheader(L('Raw data', '元データ'))
    st.write(df[filt])



### Summary dataframe created to show count and sum$ by Subscribed status
summary_df = df[filt].groupby('subscribed')['subscription_cost'].agg(['count','sum'])
summary_df['sum'] = summary_df['sum'].apply(lambda x: money(x))
#now formatted as a string (f)
#leading dollar sign, add commas, round result to 0 decimal places
my_slot2.write(summary_df.sort_index(ascending=False))  #display in order of TRUE, MAYBE, FALSE, blank




### Export the df with any changes the user made 
st.sidebar.subheader(L('Export spreadsheet with any changes', '変更を反映したスプレッドシートを書き出す'))
sidebar_changessummary_slot = st.sidebar.empty()
with sidebar_changessummary_slot:
    with st.expander(L("Show the changes made", "行った変更を表示")):
        if st.session_state.to_true:
            st.write(L("Titles you changed to TRUE ", "TRUE に変更したタイトル "), st.session_state.to_true)
        if st.session_state.to_false:
            st.write(L("Titles you changed to FALSE ", "FALSE に変更したタイトル "), st.session_state.to_false)
        if st.session_state.to_maybe:
            st.write(L("Titles you changed to MAYBE ", "MAYBE に変更したタイトル "), st.session_state.to_maybe)
        if st.session_state.to_blank:
            st.write(L("Titles you changed to (blank) ", "（空欄）に変更したタイトル "), st.session_state.to_blank)


##### Export the dataset with any changes made by user #####
@st.cache
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv=convert_df(df)

date = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")

st.sidebar.download_button(label=L("Click to download", "クリックしてダウンロード"),
                      data=csv,
                      file_name='UnsubExtender_output_'+date+'.csv',
                      mime='text/csv')


########  Charts start here  ########
st.subheader(L('Start by looking at the overall usage', '全体の利用状況を見る'))
#weighted usage in log by cost (x), colored by subscribed
#adding clickable legend to highlight subscribed categories
selection1 = alt.selection_multi(fields=['subscribed'], bind='legend')
weighted_vs_cost = alt.Chart(df[filt]).mark_point(size=75, opacity=0.5, filled=True).encode(
    alt.X('subscription_cost:Q', title=L('Journal Cost', 'ジャーナルの費用'), axis=money_axis(), scale=alt.Scale(clamp=True)),
    alt.Y('usage:Q', scale=alt.Scale(type='log'), title=WU_TITLE),
    color=alt.condition(selection1, alt.Color('subscribed:N', scale=subscribed_colorscale, title=SUB_TITLE), alt.value('lightgray')),   #Nominal data type
    shape=alt.Shape('subscribed:N', scale=subscribed_point_mapping, title=SUB_TITLE),
    tooltip=['title','downloads','citations','authorships','usage','subscription_cost', 'use_oa_percent', 'free_instant_usage_percent', 'cpu', 'cpu_rank', 'subscribed'],
    ).interactive().properties(
        height=500,
        title={
            "text": [L("Total Weighed Usage vs. Cost, color-coded by Subscribed status; clickable legend", "利用量の合計 vs. コスト（購読の値で色分け・凡例クリックで強調）")],
            "subtitle": [L("Graph supports pan, zoom, and live-updates from changes in filters on left sidebar", "グラフはパン・ズームに対応し、左サイドバーの絞り込みに連動して更新されます"), L("Journals on the underside of this curve might be considered for cancellation", "この曲線の下側にあるジャーナルは、解約の検討対象になりえます")],
            "color": "black",
            "subtitleColor": "gray"
        }
        ).add_selection(selection1)
st.altair_chart(weighted_vs_cost, use_container_width=True)
explain('usage_cost')

#same chart as Weighted Use vs. cost but now colored by cpu_rank, and would really like buckets somehow
selection2 = alt.selection_multi(fields=['subscribed'], bind='legend')
weighted_vs_cost2 = alt.Chart(df[filt]).mark_point(size=75, opacity=0.5, filled=True).encode(
    alt.X('subscription_cost:Q', title=L('Journal Cost', 'ジャーナルの費用'), axis=money_axis(), scale=alt.Scale(clamp=True)),
    y=alt.Y('usage:Q', scale=alt.Scale(type='log'), title=WU_TITLE),
    color=alt.condition(selection2, alt.Color('cpu_rank:Q', title=L('CPU Rank', 'CPUランク'), scale=alt.Scale(scheme='viridis', reverse=True)), alt.value('lightgray')),   #selection, if selected, if NOT selected,
    shape=alt.Shape(
        'subscribed:N',
        #sort=['TRUE', 'FALSE', 'MAYBE'],
        scale=subscribed_point_mapping,
        title=SUB_TITLE
        ),      #circle, square, cross, diamond, triangle-up, triangle-down, triangle-right, triangle-left
    tooltip=['title','downloads','citations','authorships','usage','subscription_cost', 'cpu', 'cpu_rank', 'subscribed'],
    ).interactive().properties(
        height=500,
        title={
            "text": [L('Total Weighted Usage vs. Cost, color coded by CPU_Rank gradient', '利用量の合計 vs. コスト（CPUランクのグラデーションで色分け）')],
            "subtitle": [L("Same graph as above, but with different color coding", "上と同じグラフで、色分けだけを変えています"), L("High Cost-per-Use rank (least economical) journals show up in darker colors", "CPUランクが高い（コスト効率が悪い）ジャーナルほど濃い色で表示されます")],
            "color": "black",
            "subtitleColor": "gray"
        }
        ).add_selection(selection2)
st.altair_chart(weighted_vs_cost2, use_container_width=True)
explain('usage_cost_rank')



st.subheader(L('Look into the authorships, citations, and downloads of each journal', '各ジャーナルのオーサーシップ・被引用・ダウンロードを見る'))
auth_hist = alt.Chart(df[filt].reset_index()).mark_bar(width=10).encode(
    alt.X('authorships:Q', title=L("Authorships (average per year over the next five years)", "オーサーシップ数（今後5年間の年平均）")),
    alt.Y('count()', title=L('Count of Records', 'ジャーナル数'), axis=alt.Axis(grid=False)),
    alt.Detail('index'),
    tooltip=['title', 'authorships', 'subscription_cost', 'subscribed'],
    color=alt.Color('subscribed:N', scale=subscribed_colorscale, title=SUB_TITLE)
    ).interactive().properties(
        height=400,
        title={
            "text": [L("Authorships Distribution", "オーサーシップ数の分布")],
            "subtitle": [L("What do the range of Authorships look like?", "オーサーシップ数はどのような範囲に分布しているでしょうか？"), L("Use this graph to help set the Authorships slider filter and narrow down titles of interest", "このグラフを見ながらオーサーシップのスライダーを設定し、注目するタイトルを絞り込みます")],
            "color": "black",
            "subtitleColor": "gray"
        }
        )
st.altair_chart(auth_hist, use_container_width=True)
explain('authorships')

scatter_dl_vs_cit = alt.Chart(df[filt]).mark_point(size=75, opacity=0.5, filled=True).encode(
    alt.X('downloads:Q', title=L("Downloads", "ダウンロード数")),
    alt.Y('citations:Q', title=L("Citations", "被引用数")),
    color=alt.Color('subscribed:N', scale=subscribed_colorscale, title=SUB_TITLE),
    shape=alt.Shape('subscribed:N', scale=subscribed_point_mapping, title=SUB_TITLE),
    tooltip=['title', 'downloads','citations', 'authorships', 'subscription_cost', 'subscribed']
    #size=('authorships')
).interactive().properties(
        height=400,
        title={
            "text": [L("Citations vs. Downloads", "被引用数 vs. ダウンロード数")],
            "subtitle": [L("What is contributing to the weighted usage?", "利用量に何が寄与しているでしょうか？"), L("Hold authorships steady with a filter and consider citations and DLs within that group", "フィルターでオーサーシップ数をそろえたうえで、そのグループ内の被引用数とDLを比べます")],
            "color": "black",
            "subtitleColor": "gray"
        }
        )
st.altair_chart(scatter_dl_vs_cit, use_container_width=True)
explain('dl_cit')


#3x scatter matrix showing all metrics vs. overall usage
scatter_selection = alt.selection_multi(fields=['subscribed'], bind='legend')

linked = alt.Chart(df[filt].rename(columns=LINK_COLS)).mark_point(size=50, opacity=0.5, filled=True).encode(
    alt.X(alt.repeat("repeat"), type='quantitative'),
    alt.Y('usage:Q', title=WU_TITLE),
    color=alt.condition(scatter_selection, alt.Color('subscribed:N', scale=subscribed_colorscale, title=SUB_TITLE), alt.value('lightgray')),   #Nominal data type
    shape=alt.Shape('subscribed:N', scale=subscribed_point_mapping, title=SUB_TITLE),
    tooltip=[LINK_COLS.get(_c, _c) for _c in ['title','downloads','citations','authorships','usage','use_oa_percent', 'free_instant_usage_percent', 'subscription_cost', 'cpu', 'cpu_rank', 'subscribed']]    
).properties(
    width=350,
    height=250,
).repeat(
    repeat=[LINK_COLS.get(_c, _c) for _c in ['downloads', 'citations', 'authorships', 'free_instant_usage_percent']],
    columns=2
).properties(
    title={
        "text": [L("Four linked plots - Weighted usage vs. [ DL / cit / auth / Free% (OA+backfile) ]", "連動する4つのグラフ - 利用量 vs. [DL / 被引用 / オーサーシップ / フリー率%]")],
        "subtitle": [L("Zooming in will adjust all four", "ズームすると4つすべてが連動して変わります")],
        'color':'black',
        'subtitleColor': 'gray'
        }
).interactive().add_selection(scatter_selection)

linked

explain('linked')



# Instant Fill % graphs
st.subheader(L('Consider the Instant Fill % from each journal (paid usage / total package usage)', '各ジャーナルのアクセス充足率（IF%）を見る（有料での利用 / パッケージ全体の利用）'))

IF_selection = alt.selection_single()

IF = alt.Chart(df[filt]).mark_point(opacity=0.5, filled=True).encode(
    alt.X('subscription_cost', title=L("Journal Cost", "ジャーナルの費用"), axis=money_axis()),    #grouped thousands with two significant digits
    alt.Y('IF%', title=L('Instant Fill %', 'アクセス充足率 (IF%)')),
    tooltip=(['title','subscription_cost','IF%']),
    color=alt.Color('subscribed:N', scale=subscribed_colorscale, title=SUB_TITLE),
    shape=alt.Shape('subscribed:N', scale=subscribed_point_mapping, title=SUB_TITLE),
    ).interactive().properties(
        height = 400,
        title={
            "text": [L('Instant Fill % vs. Journal Subscription Cost', 'アクセス充足率 vs. ジャーナルの購読費用')],
            "subtitle": [L("Which journals increase Instant Fill % the most (moving up), and what do they cost?", "どのジャーナルがアクセス充足率を最も押し上げるか（上に行くほど大きい）、その費用はいくらか？"), L("Could look for a less expensive journal that gets you the same IF%, generally the upper band", "同じIF%を得られて、より安価なジャーナル（一般に上の帯）を探せます"), L("Note: Must look at all journals in the package together; graphing subsets will throw the calculations off", "注意：パッケージ内のすべてのジャーナルをまとめて見る必要があります。一部だけで描画すると計算結果がずれます")],
            "color": "black",
            "subtitleColor": "gray"
        }
        )
st.altair_chart(IF, use_container_width=True)
explain('if_cost')

IF2 = alt.Chart(df[filt]).mark_point(opacity=0.5, filled=True).encode(
    alt.X('cost_per_IF%', scale=alt.Scale(type='log'), title=L("log ( Price per 1 IF% point)", "log（IF% 1ポイントあたりの価格）"), axis=money_axis()),
    alt.Y('IF%', title=L("Instant Fill %", "アクセス充足率 (IF%)")),
    tooltip=(['title','subscription_cost','IF%','cost_per_IF%']),
    color=alt.Color('subscribed:N', scale=subscribed_colorscale, title=SUB_TITLE),
    shape=alt.Shape('subscribed:N', scale=subscribed_point_mapping, title=SUB_TITLE)
    ).interactive().properties(
        height=400,
        title={
            "text": [L('Instant Fill % vs. Price per 1 IF% point', 'アクセス充足率 vs. IF% 1ポイントあたりの価格')],
            "subtitle": [L("Normalized by price, which journals are the best way to increase Instant Fill % (tending to upper left corner)?", "価格で正規化すると、どのジャーナルがアクセス充足率を上げる最良の手段か？（左上ほど良い）"), L("Note: X-axis shown in log to stretch and increase visibility", "注意：見やすくするため、X軸は対数で表示しています"), L("Note: Must look at all journals in the package together; graphing subsets will throw the calculations off", "注意：パッケージ内のすべてのジャーナルをまとめて見る必要があります。一部だけで描画すると計算結果がずれます")],
            "color": "black",
            "subtitleColor": "gray"
        }
)
st.altair_chart(IF2, use_container_width=True)
explain('if_price')



st.subheader(L('Look where journal decisions land in the Unsub histogram', '各ジャーナルの判断が Unsub のヒストグラムのどこにあるかを見る'))
#Unsub histogram, but colored by subscribed
unsub_hist = alt.Chart(df[filt].reset_index()).mark_bar().encode(   #.reset_index() turns the indx into a column
    alt.X('cpu:Q', bin=alt.Bin(step=HIST_STEP), title=L("Cost per Use bins (data may continue beyond the chart, zoom out or scroll to see)", "利用単価（CPU）の区間（範囲外は縮小して確認）"), axis=money_axis(',.0f', '$'), scale=alt.Scale(domain=HIST_DOMAIN)),
    alt.Y('count()', title=L('Count of Records', 'ジャーナル数'), axis=alt.Axis(grid=False)),
    alt.Detail('index'),
    tooltip=['title', 'cpu', 'cpu_rank', 'subscription_cost', 'subscribed'],
    color=alt.Color('subscribed:N', scale=subscribed_colorscale, title=SUB_TITLE)
    ).interactive().properties(
        height=400,
        title={
            "text": [L("Unsub's Cost per Use Histogram, color coded by Subscribed status", "Unsub の利用単価（CPU）ヒストグラム（購読の値で色分け）")],
            "subtitle": [L("Note: Journals are grouped by Subscribed status, not shown in continuous order by CPU like Unsub does", "注意：Unsub のようにCPU順に連続して並べるのではなく、購読の値ごとにまとめて表示しています"), L("Note 2: X-axis default set to max of " + HIST_MAX_EN + ", zoom out to see data that may have even higher CPU", "注意2：X軸は初期状態で最大 " + HIST_MAX_JA + " までです。それ以上のCPUのデータは、縮小して確認してください")],
            "color": "black",
            "subtitleColor": "gray"
        }
        )
st.altair_chart(unsub_hist, use_container_width=True)
explain('cpu_hist')



st.subheader(L('Consider journal subject areas', 'ジャーナルの主題分野を見る'))

def split_era(sentence):
    """
    Input: era_subjects column of one row
        ex. [['0608', 'Zoology'], ['0707', 'Veterinary Sciences'], ['06', 'Biological Sciences'], ['07', 'Agricultural and Veterinary Sciences']]"
    Output: a list of the broadest two digit era_subjects category; can have multiple
        ex. ['Biological Sciences', 'Agricultural and Veterinary Sciences']
    """

    two_digit_list = []
    final = []
    
    mylist = re.split(r'\]',sentence)      #breaks into [['0608', 'Zoology' (no end bracket)
    for i in mylist:
        m = re.search(r'\d+', i)    #m tells if it has digits
        if m==None:
            m = re.search(r'MD', i)
        if m!=None:             #when digit search doesn't match, it returns a NoneType and errors the group() call
            #print(m.group())    #returns the part of string where there was a match; 0608, 0707, 06, 07
            if len(m.group())==2:
                two_digit_list.append(i)
        
        
    #print(two_digit_list)     #List of two digit codes: ['06', 'Biological Sciences'
    
    for j in two_digit_list:
        comma_split = re.split(r'\',', j)
        for c in comma_split:       #either numbers or words
            d = re.search(r'[a-z]+', c)     #look for words
            if d!=None:
                final.append(c[2:-1])       #if it has words, strip off leading _' and trailing '
    
    return (final)


if ('era_subjects' in df.columns): #& (df['era_subjects'] != 0).all():
    st.markdown(L("#### :rotating_light: Alert :rotating_light:", "#### :rotating_light: 注意 :rotating_light:"))
    st.write(L("Your file is using the old **'era_subject'** column which is deprecated by Unsub since May 2022.",
               "お使いのファイルは、2022年5月以降 Unsub で廃止された旧形式の **'era_subject'** 列を使っています。"))
    st.write(L("Export files now use the **'subject', 'subject_top_three,** and **'subjects_all** codes from OpenAlex.",
               "現在のエクスポートファイルでは、OpenAlex の **'subject'、'subject_top_three'、'subjects_all'** の分類コードが使われています。"))
    st.write(L("Currently, Unsub Extender will still plot the 'era_subject column, but will eventually remove this support.",
               "現時点では Unsub Extender は 'era_subject' 列もグラフ化しますが、将来的にこの対応は廃止される予定です。"))
     
    #create new column called 'era_split', calling fn on each row and adding the two digit codes in list form
    df['era_split'] = df.apply(lambda x: split_era(x['era_subjects']), axis=1, result_type='reduce')
    #remove leading and ending bracket and quote mark
    df['era_split'] = df['era_split'].astype(str).str.slice(2,-2)
    #Now it looks like "Commerce, Management, Tourism and Services', 'Built Environment and Design', 'Engineering"
    
    #can't just split by comma since some subjects have multiple words so have to split by ', ' quotecommaspacequote
    df['era_split_by_quotecommaquote'] = df['era_split'].str.split('\', \'')
    df2 = df.explode('era_split_by_quotecommaquote')    #new df defined with more rows than the original, with repeated rows, names and all its data every time
    df2.reset_index(drop=True, inplace=True)
    
    #force 'subscribed' column to be a string, not Bool, and all uppercase
    df2['subscribed'] = df2['subscribed'].astype(str)
    df2['subscribed'] = df2['subscribed'].str.upper()
    df2['cpu_rank'] = df2['cpu_rank'].astype(int)
    
    subject_filtered_titles_df = df2.loc[df2['title'].isin(df[filt]['title'])]  #df2 is larger than df b/c rows repeated multiple times.
    #Want to show only titles that fit filter but can't apply it directly since index won't match. So only select titles that get returned in df[filt]
    
    cpurank_vs_subject2 = alt.Chart(subject_filtered_titles_df.assign(subject_disp=subject_filtered_titles_df['era_split_by_quotecommaquote'].map(subject_label))).mark_point(size=40, opacity=0.5, filled=True).encode(
        x=alt.X('subject_disp:N', title=None, axis=alt.Axis(labelLimit=260)),
        y=alt.Y('cpu_rank:Q', title=L('CPU Rank', 'CPUランク')),
        color=alt.Color('subscribed:N', scale=subscribed_colorscale, title=SUB_TITLE),   #Nominal data type
        shape=alt.Shape('subscribed:N', scale=subscribed_point_mapping, title=SUB_TITLE),
        tooltip=['title', 'cpu_rank', 'downloads','citations','authorships','usage','subscription_cost', 'era_split', 'subscribed'],
        
        ).interactive().properties(
            height=800,
            title={
                "text": [L("Overview of cancellations by 'Subject' column", "'Subject' 列による解約状況の概観")],
                "subtitle": [L("Review decisions and make sure you're not penalizing one discipline too much", "判断を見直し、特定の分野に偏って不利になっていないかを確認します"), L("Subject area classifications are probably not perfect, but gives a general idea", "主題分野の分類は完全ではありませんが、おおよその傾向をつかめます")],
                "color": "black",
                "subtitleColor": "gray"
            }
            ).configure_axis(
    labelFontSize=15,
    #titleFontSize=20
    )
    st.altair_chart(cpurank_vs_subject2, use_container_width=True)
    explain('subject')
    
#if (df['subject'] != 0).all():
elif ('subject' in df.columns):
    #cpu_Rank y vs. subject, colored by subscribed
    cpurank_vs_subject = alt.Chart(df[filt].assign(subject_disp=df[filt]['subject'].map(subject_label))).mark_point(size=40, opacity=0.5, filled=True).encode(
        x=alt.X('subject_disp:N', title=None, axis=alt.Axis(labelLimit=260)),# axis=alt.Axis(values=[0], ticks=True, grid=False, labels=False), scale=alt.Scale()),
        y=alt.Y('cpu_rank:Q', title=L('CPU Rank', 'CPUランク')),
        color=alt.Color('subscribed:N', scale=subscribed_colorscale, title=SUB_TITLE),   #Nominal data type
        shape=alt.Shape('subscribed:N', scale=subscribed_point_mapping, title=SUB_TITLE),
        tooltip=['title','downloads','citations','authorships','usage','subscription_cost', 'subscribed'],
        ).interactive().properties(
            height=800,
            title={
                "text": [L("Overview of cancellations by 'Subject' column", "'Subject' 列による解約状況の概観")],
                "subtitle": [L("Review decisions and make sure you're not penalizing one discipline too much", "判断を見直し、特定の分野に偏って不利になっていないかを確認します"), L("Subject area classifications are probably not perfect, but gives a general idea", "主題分野の分類は完全ではありませんが、おおよその傾向をつかめます")],
                "color": "black",
                "subtitleColor": "gray"
            }
            ).configure_axis(
    labelFontSize=15,
    #titleFontSize=20
    )
    st.altair_chart(cpurank_vs_subject, use_container_width=True)
    explain('subject')
else:
    st.write(L("Sorry, you don't seem to have the right data in your file.", "申し訳ありません。ファイルに必要なデータが含まれていないようです。"))
    st.write(L("I need an **era_subjects** column (old version) or a **subject** or **subject_top_three** column (May 2022+) to show these by-subject charts.",
               "主題分野別のグラフを表示するには、**era_subjects** 列（旧形式）、または **subject** もしくは **subject_top_three** 列（2022年5月以降の形式）が必要です。"))




##### Footer in sidebar #####
st.sidebar.markdown(L("### Honors and Awards", "### 受賞歴（元プロジェクト）"))
st.sidebar.markdown("- 2022 RUSA ETS [Best Emerging Technology Application](https://rusaupdate.org/2022/03/2022-ets-best-emerging-technology-application-award/) Award")
st.sidebar.markdown("- 2022 ASEE ELD [Innovation in Access to Engineering Information](https://sites.asee.org/eld/about-the-eld/awards/#innovation) Award")


st.sidebar.subheader(L("About", "このアプリについて"))
github = "[![GitHub repo stars](https://img.shields.io/github/stars/eschares/unsub_extender?logo=github&style=social)](<https://github.com/eschares/unsub_extender>)"
twitter = "[![Twitter Follow](https://img.shields.io/twitter/url?label=Twitter%20%40eschares&style=social&url=https%3A%2F%2Ftwitter.com%2Feschares)](<https://twitter.com/eschares>)"
zenodo = "[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5167933.svg)](https://doi.org/10.5281/zenodo.5167933)"
mastodon = "[![Mastodon Follow](https://img.shields.io/mastodon/follow/108216956438964080?domain=https://scholar.social&style=social)](<https://scholar.social/@eschares>)"

st.sidebar.write(zenodo)
st.sidebar.write(mastodon + " " + github)
#st.sidebar.write(twitter)

html_string = L(
    "<p style=font-size:13px>v1.1, last modified Dec. 4, 2025 <br />Created by Eric Schares, Iowa State University <br /> Send any feedback, suggestions, bug reports, or success stories to <b>eschares@iastate.edu</b><br /><br />Japanese / English switch: unofficial modified version (AGPL-3.0)</p>",
    "<p style=font-size:13px>v1.1（原版）、最終更新 2025年12月4日 <br />原作：Eric Schares（アイオワ州立大学）<br />原版へのご意見・要望・不具合報告は <b>eschares@iastate.edu</b> 宛にお送りください。<br /><br />日本語/英語切り替え対応：非公式の改変版です（AGPL-3.0）。日本語表示に関する不具合は、原作者ではなく、この改変版の提供元にお問い合わせください。</p>")
st.sidebar.markdown(html_string, unsafe_allow_html=True)
st.sidebar.markdown(L('Source code of this Japanese edition (AGPL-3.0): [GitHub](https://github.com/KKasama/Unsub_extender_ja)',
                      'この日本語版のソースコード（AGPL-3.0）：[GitHub](https://github.com/KKasama/Unsub_extender_ja)'))

# NOTE: The original app embedded third-party web-analytics snippets (Clicky and StatCounter)
# registered to the original author's accounts. They were removed in this modified version
# so that usage of this copy is not reported to those accounts.
