# Research in the Age of AI

연구자와 박사과정 학생을 위한 정적 사이트입니다. Simon Oh의 발표를 바탕으로 만들었습니다.
강의 사이트의 레이아웃을 사용하며, 강조색은 Clay `#d4613e`입니다.

## 로컬 실행

Ruby와 Bundler가 필요합니다. `Gemfile`은 GitHub Pages와 같은 Jekyll 3.10.0을 지정합니다.

```bash
bundle install
bundle exec jekyll serve --host 127.0.0.1 --port 4176
```

브라우저에서 `http://127.0.0.1:4176`을 엽니다.

## 내용 수정

`_data/sections.yml`에는 탭과 하위 페이지의 순서가 있습니다.
`_data/readings.yml`에는 읽을거리가 한 항목당 한 줄로 저장됩니다.
`year`는 정수로 유지합니다. 공개 링크가 없으면 `url`은 빈 문자열로 둡니다.
경제 논문은 `group` 값으로 네 묶음에 나눕니다. 각 묶음 안에서는 오래된 자료부터 표시합니다.

본문은 `index.md`와 `tool/`, `topic/`, `substitute/`, `infrastructure/`의 Markdown 파일에 있습니다.
공통 화면은 `_layouts/`, `_includes/`, `assets/site.css`에서 관리합니다.

## 검증

```bash
bundle exec jekyll build
python3 scripts/check.py
python3 -m venv .venv
.venv/bin/pip install -r requirements-test.txt
.venv/bin/python -m playwright install chromium
```

서버를 실행한 상태에서 다음 명령을 사용합니다.

```bash
.venv/bin/python scripts/browser_check.py
.venv/bin/python scripts/check_urls.py
```

첫 번째 검사는 탭 순서, 하위 페이지, 내부 링크, 자료 수를 확인합니다.
브라우저 검사는 1280, 1024, 820, 390, 320px에서 모든 페이지를 확인합니다.
주요 네 페이지의 스크린샷은 1280, 390, 320px에서 `evidence/`에 저장합니다.
외부 링크 검사는 응답 코드를 기록합니다. 200이 아닌 응답은 직접 확인해야 합니다.

원격 저장소와 배포 설정은 포함하지 않았습니다.
