# 쿠팡파트너스 키워드 생성기

쿠팡파트너스 포스팅 작성을 위한 롱테일 키워드 생성 도구입니다. PySide6를 사용한 GUI 애플리케이션으로, Gemini 또는 OpenAI를 활용하여 검색량이 적당하고 경쟁이 낮은 롱테일 키워드를 자동으로 생성합니다.

## 기능

- **카테고리 입력**: 생활가전, 육아 제품, 디지털 액세서리 등 다양한 카테고리 지원
- **롱테일 키워드 생성**: LLM을 활용하여 구매 의도가 있는 롱테일 키워드 10-15개 자동 생성
- **다중 LLM 지원**: Gemini 또는 OpenAI 선택 가능
- **사용자 친화적 GUI**: 직관적인 PySide6 기반 인터페이스

## 설치

### 1. 의존성 설치

```bash
pip install -e .
```

또는 직접 설치:

```bash
pip install PySide6 google-generativeai openai
```

### 2. API 키 설정

#### Gemini 사용 시

환경변수로 설정:
```bash
# Windows (CMD)
set GEMINI_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:GEMINI_API_KEY="your_api_key_here"

# Linux/Mac
export GEMINI_API_KEY=your_api_key_here
```

또는 `.env` 파일 생성 (Python-dotenv 사용 시):
```
GEMINI_API_KEY=your_api_key_here
```

#### OpenAI 사용 시

환경변수로 설정:
```bash
# Windows (CMD)
set OPENAI_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:OPENAI_API_KEY="your_api_key_here"

# Linux/Mac
export OPENAI_API_KEY=your_api_key_here
```

또는 `.env` 파일 생성:
```
OPENAI_API_KEY=your_api_key_here
```

## 사용 방법

1. 애플리케이션 실행:
   ```bash
   python main.py
   ```

2. 카테고리 입력:
   - 예: `공기청정기`, `가습기`, `히터`, `선풍기`
   - 예: `아기 식탁의자`, `수유쿠션`, `카시트`
   - 예: `마이크`, `웹캠`, `키보드`, `마우스`

3. LLM 제공자 선택:
   - 드롭다운에서 `Gemini` 또는 `OpenAI` 선택

4. 키워드 생성:
   - "키워드 생성" 버튼 클릭
   - 생성된 롱테일 키워드가 텍스트 영역에 표시됩니다

## 지원 카테고리 예시

### 생활가전
- 공기청정기
- 가습기
- 히터
- 선풍기

### 육아 제품
- 아기 식탁의자
- 수유쿠션
- 카시트

### 디지털 액세서리
- 마이크
- 웹캠
- 키보드
- 마우스

## 요구사항

- Python 3.12.12 이상
- PySide6 6.6.0 이상
- google-generativeai 0.3.0 이상 (Gemini 사용 시)
- openai 1.0.0 이상 (OpenAI 사용 시)

## 라이선스

이 프로젝트는 개인 사용 목적으로 제작되었습니다.

