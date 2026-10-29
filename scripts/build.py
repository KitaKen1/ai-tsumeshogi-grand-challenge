#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render a static, unnumbered catalogue from curated source-backed data."""
import html,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'data/challenges.json').read_text(encoding='utf-8'))
TASKS=DATA['challenges'];SOURCES={x['id']:x for x in DATA['sources']}
COMPUTER_HEADING='AI・コンピューターによる達成例'
LABELS={'computer':'AI・コンピューター達成例あり','human':'人間達成・AI・コンピューター未確認','frontier':'双方の達成例未確認'}
def esc(x):return html.escape(str(x),quote=True)
def stage(t):return 'computer' if t['ai_status']=='reported' else 'human' if t['human_status']=='reported' else 'frontier'
def refs(ids):return ''.join(f' <a class="reference" href="{esc(SOURCES[i]["url"])}" aria-label="{esc(SOURCES[i]["title"])}" title="{esc(SOURCES[i]["title"])}">出典</a>' for i in ids)
def main():
    assert len(TASKS)==len({t['id'] for t in TASKS})==len({t['title'] for t in TASKS})==DATA["expected_count"]
    assert all('number' not in t for t in TASKS)
    counts=Counter(stage(t) for t in TASKS);categories=list(dict.fromkeys(t['category'] for t in TASKS))
    rows=[];sections=[];markdown=[]
    for t in TASKS:
        for key in ['existing_sources','ai_sources','ai_detail_sources']:assert all(i in SOURCES for i in t.get(key,[]))
        s=stage(t);achieved=s=='computer';assert bool(t['ai_summary'])==achieved
        assert not achieved or t['ai_sources']
        assert t['human_example'] and t['benchmark']
        assert bool(t['computer_example']) == bool(t['computer_benchmark']) == achieved
        ai=f'{esc(t["computer_example"])}{refs(t["ai_sources"])}<small>{esc(t["ai_method"])}</small>' if achieved else '<span aria-label="達成例未確認">—</span>'
        search=' '.join(str(t.get(k,'')) for k in ['title','target','category','task_type','human_example','benchmark','ai_summary','example_year'])
        attrs=f'data-stage="{s}" data-category="{esc(t["category"])}" data-year="{t.get("example_year") or 0}" data-search="{esc(search)}"'
        baseline='<small>比較基準・参考報告</small>' if s=='frontier' else ''
        rows.append(f'''<tr {attrs} data-task="{esc(t['id'])}"><th scope="row"><a class="challenge-link" href="#{esc(t['id'])}">{esc(t['title'])}</a><div class="row-tags"><span class="stage {s}">{LABELS[s]}</span><span class="type">{esc(t['task_type'])}</span></div></th><td>{esc(t['human_example'])}{refs(t['existing_sources'])}</td><td class="benchmark">{esc(t['benchmark'])}</td><td class="ai-result" data-achieved="{str(achieved).lower()}">{ai}</td><td class="computer-benchmark">{esc(t["computer_benchmark"]) if achieved else "—"}</td></tr>''')
        computer_block=''
        if achieved:computer_block=f'<h3>{COMPUTER_HEADING}</h3><p>{esc(t["ai_summary"])}{refs(t["ai_sources"])}</p><p class="method">{esc(t["ai_method"])}</p>'
        if t.get('ai_detail'):
            heading='補足' if achieved else '関連報告（達成例とは別）'
            computer_block+=f'<h3>{heading}</h3><p>{esc(t["ai_detail"])}{refs(t.get("ai_detail_sources",[]))}</p>'
        criteria=''.join(f'<li>{esc(x)}</li>' for x in t['success_conditions'])
        sections.append(f'''<section class="challenge" id="{esc(t['id'])}" {attrs} aria-labelledby="title-{esc(t['id'])}"><header class="section-header"><h2 id="title-{esc(t['id'])}">{esc(t['title'])}</h2><a class="back" href="#overview">一覧へ ↑</a></header><p class="detail-tags"><span class="stage {s}">{LABELS[s]}</span> <span class="type">{esc(t['task_type'])}</span></p><p class="challenge-description">{esc(t['target'])}</p><h3>比較基準</h3><p>{esc(t['benchmark'])}</p><h3>この条件にする理由</h3><p>{esc(t['condition_rationale'])}</p><h3>{'比較基準・参考報告' if s=='frontier' else '人間の到達例・評価の根拠'}</h3><p>{esc(t['existing_detail'])}{refs(t['existing_sources'])}</p><p class="value-basis">{esc(t['value_basis'])}</p>{('<p class="record-note">'+esc(t['claim_notes'])+'</p>') if t.get('claim_notes') else ''}{computer_block}<h3>確認条件</h3><ul>{criteria}</ul></section>''')
        links=' '.join(f'[{SOURCES[i]["title"]}]({SOURCES[i]["url"]})' for i in t['existing_sources'])
        markdown.append(f'| [{t["title"]}](#{t["id"]})<br>{LABELS[s]} | {t["human_example"]} {links} | {t["benchmark"]} | {t["computer_example"] if achieved else "—"} | {t["computer_benchmark"] if achieved else "—"} |')
    options=''.join(f'<option value="{esc(c)}">{esc(c)}</option>' for c in categories)
    source_list=''.join(f'<li><a href="{esc(x["url"])}">{esc(x["title"])}</a><small>{esc(x["kind"])}</small></li>' for x in SOURCES.values())
    rules=''.join(f'<li>{esc(v)}</li>' for v in DATA['common_rules'].values())
    document=f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(DATA['title'])}</title><meta name="description" content="人間の到達例、AI・コンピューターの達成例、未達目標を整理した詰将棋創作{len(TASKS)}課題。"><meta name="theme-color" content="#ffffff"><link rel="stylesheet" href="assets/style.css"><script src="assets/filter.js" defer></script></head><body id="top"><a class="skip" href="#overview">課題一覧へ</a><main>
    <header class="intro"><h1>{esc(DATA['title'])}</h1><p class="lead">詰将棋創作の{len(TASKS)}課題。</p><p class="meta">資料確認：<time datetime="{DATA['reviewed_on']}">{DATA['reviewed_on']}</time></p></header>
    <aside class="highlights" aria-labelledby="recent-title"><h2 id="recent-title">最近の到達例</h2><ul><li><a href="#royal-succession">「王位継承」：都玉の交代</a><small>2026年看寿賞</small></li><li><a href="#record-2-11">受方六種不成19手</a><small>2026年発表</small></li><li><a href="#record-4-32">攻方馬77回連続移動</a><small>2026年発表</small></li><li><a href="#record-2-12">「ツインレイ」：半自動逆算の双玉煙</a><small>2025年発表</small></li></ul></aside>
    <section id="overview" aria-labelledby="overview-title"><h2 id="overview-title">チャレンジ一覧</h2><div class="stage-summary" aria-label="到達状況で絞り込み"><button type="button" data-preset="frontier">双方の達成例未確認 <strong>{counts['frontier']}</strong></button><button type="button" data-preset="human">人間達成・計算機未確認 <strong>{counts['human']}</strong></button><button type="button" data-preset="computer">AI・コンピューター達成 <strong>{counts['computer']}</strong></button></div>
    <form class="filters" role="search" aria-label="課題の絞り込み"><label>到達状況<select id="stage"><option value="">すべて</option><option value="frontier">双方の達成例未確認</option><option value="human">人間達成・AI・コンピューター未確認</option><option value="computer">AI・コンピューター達成例あり</option></select></label><label>分野<select id="category"><option value="">すべて</option>{options}</select></label><label class="search-label">検索<input id="search" type="search" placeholder="七種合、煙詰、逆王手など"></label><label class="recent-check"><input id="recent" type="checkbox">2020年以降の作例</label><button type="reset">解除</button></form>
    <p class="result-count" id="result-count" aria-live="polite">{len(TASKS)}件を表示</p><p class="mobile-hint">表は横にスクロールできます →</p><div class="table-wrap" tabindex="0" role="region" aria-label="{len(TASKS)}課題の比較表"><table><caption class="visually-hidden">チャレンジ、人間の既存例、人間の比較基準、AI・コンピューターによる達成例、AI・コンピューターの比較基準</caption><colgroup><col class="col-challenge"><col class="col-existing"><col class="col-benchmark"><col class="col-ai"><col class="col-ai-benchmark"></colgroup><thead><tr><th scope="col">チャレンジ</th><th scope="col">人間の既存例</th><th scope="col">人間の比較基準</th><th scope="col">{COMPUTER_HEADING}</th><th scope="col">AI・コンピューターの<br>比較基準</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div><p id="no-results" hidden>該当する課題はありません。</p><p class="table-note">課題名から詳細へ。— は達成例未確認。未確認は未達の証明ではありません。</p>
    <details class="rules"><summary>新機構・記録目標・達成区分の読み方</summary><p>七種合の新機構なら10枚以上も対象です。９枚の項目は省駒部門です。４三玉・１一玉は既存例の条件で、一般の課題にそのまま課しません。</p><ul>{rules}</ul><p>「記録水準の別作」は人間の到達点に並ぶ目標で、世界記録更新の主張ではありません。登録記録は最適性の証明ではありません。回数は作意・変化など出典の集計規約に従います。到達区分は難度順そのものではありません。</p></details></section>
    <div class="details-heading"><h2>各課題の条件と根拠</h2><p>一覧に表示中の課題の詳細です。</p></div>{''.join(sections)}<section class="sources" id="sources"><details><summary>出典一覧（{len(SOURCES)}件）</summary><ul>{source_list}</ul></details></section><section class="contribute"><h2>成果の追加</h2><p>作品・検証結果・先行作との違い・AI／人間の担当範囲を添えてください。</p><a href="CONTRIBUTING.md">追加ガイド</a> <a href="data/challenges.json">元データ（JSON）</a></section></main><footer><span>{esc(DATA['title'])}</span><a href="#top">ページ上部へ ↑</a></footer></body></html>'''
    (ROOT/'index.html').write_text(document,encoding='utf-8')
    readme=f'''# {DATA['title']}

詰将棋創作の{len(TASKS)}課題。通し番号は付けず、分野・到達状況・作例の年代で絞り込めます。

- 双方の達成例未確認：{counts['frontier']}課題
- 人間の達成例あり／AI・コンピューター未確認：{counts['human']}課題
- AI・コンピューターの達成報告あり：{counts['computer']}課題

到達区分は確認した公開報告の範囲です。「未確認」を世界での不存在の証明とはしません。コンピューター欄には、対応する条件の達成報告だけを載せます。

## 条件と新規性

４三玉・１一玉は既存作の条件で、一般の課題の制約にはしません。七種合の新機構は10枚以上でも対象です。使用９枚の項目は省駒部門として区別します。

「記録水準の別作」「記録更新」「新機構」「外部評価」を区別し、条件の理由を各詳細に記載しています。作品のコピー・反転・平行移動だけを新機構とは数えません。

## 一覧

| チャレンジ | 人間の既存例 | 人間の比較基準 | {COMPUTER_HEADING} | AI・コンピューターの比較基準 |
| --- | --- | --- | --- | --- |
{chr(10).join(markdown)}

## GitHub Pagesで公開する

推奨リポジトリ名：`{DATA['repository_name']}`。生成済みのHTML・CSS・JavaScriptを配信する静的サイトです。

1. リポジトリを作り、このフォルダのファイルを `main` に追加します。
2. **Settings → Pages → Deploy from a branch** を選びます。
3. **main / (root)** を指定して保存します。

公開URL：`https://<ユーザー名>.github.io/{DATA['repository_name']}/`

[GitHub公式の公開手順](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)

## 更新する

`data/challenges.json` を編集し、`python3 scripts/build.py` でHTMLとREADMEを生成します。外部ライブラリは不要です。

ローカル表示：`python3 -m http.server 8000 --bind 127.0.0.1`。`index.html` を直接開くこともできます。

[追加・修正の基準](CONTRIBUTING.md) ／ [元データ](data/challenges.json)
'''
    for t in TASKS:
        ids=list(dict.fromkeys(t['existing_sources']+t['ai_sources']+t.get('ai_detail_sources',[])))
        links=' '.join(f'[{SOURCES[i]["title"]}]({SOURCES[i]["url"]})' for i in ids)
        readme+=f'\n<a id="{t["id"]}"></a>\n\n### {t["title"]}\n\n{t["target"]}\n\n比較基準：{t["benchmark"]}\n\n条件の理由：{t["condition_rationale"]}\n\n{t["existing"]}\n\n{t["ai_summary"] or "AI・コンピューターによる達成例：未確認。"}\n\n{links}\n'
    (ROOT/'README.md').write_text(readme,encoding='utf-8')
    print(json.dumps({'tasks':len(TASKS),'sources':len(SOURCES),'stages':dict(counts)},ensure_ascii=False))
if __name__=='__main__':main()
