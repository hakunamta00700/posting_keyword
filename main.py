"""
쿠팡파트너스 포스팅 작성 도구 - 롱테일 키워드 생성기
"""
import os
import sys
from typing import List, Optional

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QComboBox,
    QMessageBox,
    QProgressBar,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class KeywordGeneratorThread(QThread):
    """키워드 생성을 위한 백그라운드 스레드"""
    keywords_generated = Signal(list)
    error_occurred = Signal(str)
    progress_updated = Signal(str)

    def __init__(self, category: str, llm_provider: str, model: Optional[str] = None):
        super().__init__()
        self.category = category
        self.llm_provider = llm_provider
        self.model = model

    def run(self):
        """키워드 생성 실행"""
        try:
            self.progress_updated.emit("LLM에 요청 중...")
            keywords = self._generate_keywords()
            self.keywords_generated.emit(keywords)
        except KeyboardInterrupt:
            self.error_occurred.emit("사용자에 의해 작업이 취소되었습니다.")
        except Exception as e:
            self.error_occurred.emit(str(e))

    def _generate_keywords(self) -> List[str]:
        """LLM을 사용하여 롱테일 키워드 생성"""
        prompt = f"""쿠팡파트너스 포스팅을 위한 롱테일 키워드를 생성해주세요.

카테고리: {self.category}


당신은 **SEO 전문가이자 상품 검색 의도 분석 전문가**입니다.
입력된 카테고리·사용환경·특징을 기반으로 **구매 의도가 명확한 롱테일 키워드 10~15개**를 생성합니다.

## 🎯 생성 목표

* 검색량은 적당하고 경쟁이 낮은 키워드 생성
* 명확한 구매 의도 포함(추천, 비교, 가성비 등)
* 실제 사용자가 검색할 법한 자연스러운 표현
* 특정 상황·용도·문제 해결 중심의 키워드

## ✔ 생성 규칙

1. **한 줄에 한 개씩 출력**
2. **번호 없이 키워드만 출력**
3. **중복·비자연스러운 키워드 금지**
4. **3~6단어 구성**
5. **브랜드명·모델명 사용 금지**
6. **너무 짧거나 너무 긴 키워드 금지**
7. **구매 의도 단어 반드시 포함:** 추천, 비교, 가성비, 2025, TOP3, 리뷰 등
8. **상황형 요소 포함:** 원룸용, 아기방, 사무실용, 저소음, 휴대용 등
9. **제품 속성 요소 포함:** 대용량, 가열식, 초음파, 미니, 필터교체 등
10. **검색량이 너무 높은 단일 키워드 금지** (예: 공기청정기)

## 📥 입력 예시

```
카테고리: 공기청정기
사용환경: 아기방
특징: 저소음, 미세먼지 제거
```

또는

```
카테고리: 무선청소기
사용환경: 원룸
특징: 가성비, 경량
```

## 📤 출력 형식

아래 형식을 **반드시 그대로** 지킵니다.

* 번호 없음
* 한 줄에 하나씩
* 총 10~15개

## 🔥 출력 예시(참고용)

```
아기방 공기청정기 저소음 추천
원룸용 공기청정기 필터교체 쉬운 모델
공기청정기 2025 가성비 좋은 제품
소형 공기청정기 미세먼지 제거 강한 모델
아기 잠잘때 조용한 공기청정기 추천
사무실 개인용 미니 공기청정기 추천
공기청정기 가열식 vs 초음파 비교
대용량 공기청정기 원룸 추천 모델
미니 공기청정기 휴대용 가성비 추천
방 좁을 때 적합한 공기청정기 TOP3
키워드 목록:"""

        if self.llm_provider == "Gemini":
            return self._generate_with_gemini(prompt)
        elif self.llm_provider == "OpenAI":
            if not self.model:
                raise ValueError("OpenAI 모델이 선택되지 않았습니다.")
            return self._generate_with_openai(prompt, self.model)
        else:
            raise ValueError(f"지원하지 않는 LLM 제공자: {self.llm_provider}")

    def _generate_with_gemini(self, prompt: str) -> List[str]:
        """Gemini API를 사용하여 키워드 생성"""
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai 패키지가 설치되지 않았습니다.")

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY 환경변수가 설정되지 않았습니다.\n"
                "환경변수를 설정하거나 .env 파일에 GEMINI_API_KEY를 추가하세요."
            )

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        
        # 응답에서 키워드 추출
        keywords_text = response.text.strip()
        keywords = [
            line.strip()
            for line in keywords_text.split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]
        
        # 번호 제거 (예: "1. ", "1)", "- " 등)
        cleaned_keywords = []
        for keyword in keywords:
            # 번호 패턴 제거
            keyword = keyword.lstrip("0123456789. )-")
            keyword = keyword.strip()
            if keyword:
                cleaned_keywords.append(keyword)
        
        return cleaned_keywords[:15]  # 최대 15개

    def _generate_with_openai(self, prompt: str, model: str) -> List[str]:
        """OpenAI API를 사용하여 키워드 생성"""
        if not OPENAI_AVAILABLE:
            raise ImportError("openai 패키지가 설치되지 않았습니다.")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY 환경변수가 설정되지 않았습니다.\n"
                "환경변수를 설정하거나 .env 파일에 OPENAI_API_KEY를 추가하세요."
            )

        client = OpenAI(api_key=api_key)
        
        # o1, o1-mini, o1-pro, o3 모델은 구조화된 출력 모드 사용
        if model.startswith("o1") or model.startswith("o3"):
            # o1/o3 모델은 temperature 파라미터를 지원하지 않음
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 쿠팡파트너스 포스팅을 위한 롱테일 키워드 생성 전문가입니다.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
        else:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 쿠팡파트너스 포스팅을 위한 롱테일 키워드 생성 전문가입니다.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )

        keywords_text = response.choices[0].message.content.strip()
        keywords = [
            line.strip()
            for line in keywords_text.split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]
        
        # 번호 제거
        cleaned_keywords = []
        for keyword in keywords:
            keyword = keyword.lstrip("0123456789. )-")
            keyword = keyword.strip()
            if keyword:
                cleaned_keywords.append(keyword)
        
        return cleaned_keywords[:15]  # 최대 15개


class MainWindow(QMainWindow):
    """메인 윈도우"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("쿠팡파트너스 키워드 생성기")
        self.setGeometry(100, 100, 800, 600)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 레이아웃
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 제목
        title_label = QLabel("쿠팡파트너스 롱테일 키워드 생성기")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_font.setFamily("맑은 고딕")  # Windows에서 안정적인 폰트
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 카테고리 입력 섹션
        category_layout = QVBoxLayout()
        category_label = QLabel("카테고리 입력:")
        category_font = QFont("맑은 고딕", 10, QFont.Bold)
        category_label.setFont(category_font)
        category_layout.addWidget(category_label)
        
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText(
            "예: 공기청정기, 가습기, 히터, 선풍기, 아기 식탁의자, 수유쿠션, 카시트, 마이크, 웹캠, 키보드, 마우스 등"
        )
        self.category_input.setMinimumHeight(35)
        category_layout.addWidget(self.category_input)
        layout.addLayout(category_layout)
        
        # LLM 선택 섹션
        llm_layout = QVBoxLayout()
        
        # LLM 제공자 선택
        llm_provider_layout = QHBoxLayout()
        llm_label = QLabel("LLM 제공자:")
        llm_font = QFont("맑은 고딕", 10, QFont.Bold)
        llm_label.setFont(llm_font)
        llm_provider_layout.addWidget(llm_label)
        
        self.llm_combo = QComboBox()
        available_providers = []
        if GEMINI_AVAILABLE:
            available_providers.append("Gemini")
        if OPENAI_AVAILABLE:
            available_providers.append("OpenAI")
        
        if not available_providers:
            QMessageBox.warning(
                self,
                "경고",
                "LLM 라이브러리가 설치되지 않았습니다.\n"
                "pip install google-generativeai 또는 pip install openai를 실행하세요.",
            )
        
        self.llm_combo.addItems(available_providers)
        self.llm_combo.currentTextChanged.connect(self.on_llm_provider_changed)
        llm_provider_layout.addWidget(self.llm_combo)
        llm_provider_layout.addStretch()
        llm_layout.addLayout(llm_provider_layout)
        
        # OpenAI 모델 선택 (OpenAI 선택 시에만 표시)
        openai_model_layout = QHBoxLayout()
        self.openai_model_label = QLabel("OpenAI 모델:")
        self.openai_model_label.setFont(llm_font)
        self.openai_model_label.setVisible(False)
        openai_model_layout.addWidget(self.openai_model_label)
        
        self.openai_model_combo = QComboBox()
        openai_models = [
            "gpt-4",
            "gpt-4-32k",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
            "o1",
            "o1-mini",
            "o1-pro",
            "o3",
        ]
        self.openai_model_combo.addItems(openai_models)
        self.openai_model_combo.setCurrentText("gpt-4o")  # 기본값
        self.openai_model_combo.setVisible(False)
        openai_model_layout.addWidget(self.openai_model_combo)
        openai_model_layout.addStretch()
        llm_layout.addLayout(openai_model_layout)
        
        layout.addLayout(llm_layout)
        
        # 초기 상태 설정
        if self.llm_combo.count() > 0:
            self.on_llm_provider_changed(self.llm_combo.currentText())
        
        # 생성 버튼
        self.generate_button = QPushButton("키워드 생성")
        self.generate_button.setMinimumHeight(40)
        self.generate_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            """
        )
        self.generate_button.clicked.connect(self.generate_keywords)
        layout.addWidget(self.generate_button)
        
        # 진행 상태 표시
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # 무한 진행 표시
        layout.addWidget(self.progress_bar)
        
        # 키워드 출력 섹션
        result_layout = QVBoxLayout()
        result_label = QLabel("생성된 롱테일 키워드:")
        result_font = QFont("맑은 고딕", 10, QFont.Bold)
        result_label.setFont(result_font)
        result_layout.addWidget(result_label)
        
        self.keywords_output = QTextEdit()
        self.keywords_output.setPlaceholderText("생성된 키워드가 여기에 표시됩니다...")
        self.keywords_output.setReadOnly(True)
        result_layout.addWidget(self.keywords_output)
        layout.addLayout(result_layout)
        
        # 키워드 생성 스레드
        self.keyword_thread: Optional[KeywordGeneratorThread] = None

    def on_llm_provider_changed(self, provider: str):
        """LLM 제공자 변경 시 호출"""
        if provider == "OpenAI" and OPENAI_AVAILABLE:
            self.openai_model_label.setVisible(True)
            self.openai_model_combo.setVisible(True)
        else:
            self.openai_model_label.setVisible(False)
            self.openai_model_combo.setVisible(False)

    def generate_keywords(self):
        """키워드 생성 시작"""
        category = self.category_input.text().strip()
        
        if not category:
            QMessageBox.warning(self, "입력 오류", "카테고리를 입력해주세요.")
            return
        
        if self.llm_combo.count() == 0:
            QMessageBox.warning(
                self,
                "설정 오류",
                "사용 가능한 LLM 제공자가 없습니다.",
            )
            return
        
        llm_provider = self.llm_combo.currentText()
        
        # OpenAI 모델 선택 확인
        model = None
        if llm_provider == "OpenAI":
            model = self.openai_model_combo.currentText()
            if not model:
                QMessageBox.warning(self, "입력 오류", "OpenAI 모델을 선택해주세요.")
                return
        
        # UI 업데이트
        self.generate_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.keywords_output.clear()
        self.keywords_output.setPlaceholderText("키워드를 생성하는 중...")
        
        # 스레드 생성 및 시작
        self.keyword_thread = KeywordGeneratorThread(category, llm_provider, model)
        self.keyword_thread.keywords_generated.connect(self.on_keywords_generated)
        self.keyword_thread.error_occurred.connect(self.on_error)
        self.keyword_thread.progress_updated.connect(self.on_progress_updated)
        self.keyword_thread.start()

    def on_keywords_generated(self, keywords: List[str]):
        """키워드 생성 완료 처리"""
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        
        if keywords:
            keywords_text = "\n".join(f"• {keyword}" for keyword in keywords)
            self.keywords_output.setPlainText(keywords_text)
        else:
            self.keywords_output.setPlainText("생성된 키워드가 없습니다.")
            QMessageBox.information(self, "알림", "생성된 키워드가 없습니다.")

    def on_error(self, error_message: str):
        """에러 처리"""
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        self.keywords_output.setPlainText("")
        self.keywords_output.setPlaceholderText("생성된 키워드가 여기에 표시됩니다...")
        QMessageBox.critical(self, "오류", f"키워드 생성 중 오류가 발생했습니다:\n\n{error_message}")

    def on_progress_updated(self, message: str):
        """진행 상태 업데이트"""
        self.keywords_output.setPlaceholderText(message)


def main():
    """애플리케이션 진입점"""
    app = QApplication(sys.argv)
    
    # 애플리케이션 스타일 설정
    app.setStyle("Fusion")
    
    # 기본 폰트 설정 (Windows 호환성 개선)
    default_font = QFont("맑은 고딕", 9)
    app.setFont(default_font)
    
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\n애플리케이션이 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"애플리케이션 실행 중 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
