# Unsub Extender - Versioning Record and Changelog

## Japanese edition v1.1 (2026-10-31) / 日本語版 v1.1

Fixes / 修正
- Edits to the "Subscribed" status (TRUE / FALSE / MAYBE) no longer leak between users. The app now works on a private copy of the cached data, so changes made on the bundled sample (or any identical file) cannot appear for another user. / 「購読」の変更が、同じ内容のファイルを開いた別の利用者の画面に出てしまう問題を修正しました（付属サンプルなど）。人ごとにデータのコピーで作業します。
- The currency choice is now kept separately for an uploaded file (default: yen) and for the bundled sample (default: USD). Removing an uploaded file no longer leaves the USD sample displayed as yen. / 通貨の選択を、アップロードしたファイル用（初期値は円）と付属サンプル用（初期値は$）に分けました。ファイルを外したあとも、サンプルが円表示のままになりません。
- The CPU histogram now scales its bin width and initial range to the data (about 100 bins up to the 99th percentile), instead of fixed 200-yen / 1-dollar bins. This fixes the single thick bar shown when the selected currency and the data did not match, and gives a readable histogram for yen files. / 利用単価（CPU）のヒストグラムの区間の幅と表示範囲を、データに合わせて自動で決めるようにしました（上位1%の値までを約100区間に分けます）。通貨の選択とデータが合わないときに1本の太い棒になる問題を直し、円のファイルでも見やすく表示します。

Operations / 運用
- The web version runs at https://unsub-extender-jpn.ijapan.info/ and takes the latest code from this repository each time the server restarts. / Web版は https://unsub-extender-jpn.ijapan.info/ で動いており、サーバーの再起動のたびに、このリポジトリの最新のコードを取り込みます。

## Japanese edition v1.0 (2026-10, first public release) / 日本語版 v1.0（初回公開）
- Added unsub_extender_ja.py: Japanese / English interface switch, yen / dollar switch
- Added "How the numbers are calculated" section and an explanation under every graph and sidebar filter
- Terminology aligned with Unsub's Japanese interface; Japanese subject names
- More robust CSV loading (skips extra title rows, friendly error for missing columns)
- Fixed clipped text when zooming graphs
- Removed third-party web analytics (Clicky, StatCounter)
- Currency switch renamed "Currency of the amounts in your file" (no exchange-rate conversion); notes on server-side processing and a source-code link added
- Web version published; published after confirmation with the original author, Eric Schares
- Original unsub_extender.py is unchanged

## 3/24/2022, v.1.2
- add RUSA/ETS BETA award information
- add live demo webinar links
- 'perpetual_access_years' and '_text' conversions
- Support blank Subscribed status
- Logic for 'subject' and 'era_subjects' str convert

## 2/2/2022
- removed streamlit-analytics, was not compatible with Streamlit 1.3.1
- latest pandas (1.4) was causing AssertionError, downgraded to 1.3.5
- fixed trailing underscore in exported dataset filename
- added dropdown to show user what they changed before exporting new data

## 1/25/2022, v.1.1
- upgraded Streamlit from v.0.84.1 to v.1.3.1 for less memory usage (current version is v1.4, but upgraded caused error "no module named 'streamlit.report_thread'")
- streamlit.media_file_manager deprecated, move to st.download_button to export dataset
- st.beta_columns move to st.columns
- st.beta_expander move to st.expander
- add 'era_subjects' to example data file
- convert subjects and era_subjects columns to strings
- used Streamlit states to get decisions to persist across runs
- changed marker shape to vary by Subscribed status

## 8/6/2021, v.1.0
- first stable version released
- get DOI
