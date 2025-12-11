## 프로젝트 소개

EZCAM은 웹캠 실시간 배경 제거 프로그램입니다. AI 기반으로 사용자와 배경을 구분하고 웹캠의 배경을 제거합니다. 덕분에 크로마키 배경 천이 없는 상황에서 사용할 수 있어, 방송인들의 초기 투자 비용 감소와 공간 활용성을 높일 수 있습니다.

### 주요 기능

- 실시간 웹캠 배경 제거
- 두 가지 모드 지원:
  - **메인 윈도우**: 원본 화면과 크로마키 적용 화면 나란히 보기
  - **오버레이 모드**: 투명 배경의 플로팅 윈도우로 전경만 표시
- 다중 카메라 지원 및 실시간 카메라 전환
- 배경 민감도 조절 슬라이더

## 기술 스택

- Application: Python, PyQt6, Pygrabber, QtAwesome, OpenCV
- AI: PyTorch, RobustVideoMatting

### Python, PyQt6

- 프로그램 GUI 구현 및 각종 동작

### Pygrabber, OpenCV

- OpenCV (cv2.VideoCapture): 카메라를 열고 프레임을 캡처하는 용도

- Pygrabber (FilterGraph): Windows DirectShow API로 연결된 **카메라 이름 목록**을 가져오는 용도

### AI/ML

- **RobustVideoMatting (RVM)** - 실시간 비디오 매팅 모델
  - ResNet50 백본
  - 시간적 일관성을 위한 recurrent 구조로, 이전 프레임 정보를 활용해 깜빡임 없이 부드러운 실시간 배경 제거가 가능

## 설치 및 실행

1. 압축 파일 설치

[압축 파일 다운로드](https://drive.google.com/file/d/1RIlnrC7C3fiUqxpTWG-DP5WtozCc2roy/view?usp=sharing)

2. 코드 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# RVM 모델 가중치 다운로드
# rvm_resnet50.pth 파일을 프로젝트 루트에 배치
# 다운로드: https://github.com/PeterL1n/RobustVideoMatting/tree/master

# 실행이 안되는 경우 현재 폴더에 RobustVideoMatting폴더가 있는지 확인해주세요.
# 없는 경우: `git clone https://github.com/PeterL1n/RobustVideoMatting`

# 애플리케이션 실행
python main.py

# 설치 파일로 만드는 명령어
python -m PyInstaller --onedir --windowed --name="EZCAM2" --add-data "styles;styles" --add-data "rvm_resnet50.pth;." --hidden-import="RobustVideoMatting.model" main.py
```

## 기술적 어려움

### 1. 실시간 성능 최적화

**문제**: AI 모델 추론이 실시간으로 처리되어야 하는 성능 요구사항

**해결**:

- CPU대신 CUDA GPU 가속 활용
- RVM 모델의 recurrent state 재사용으로 시간적 일관성 확보
- QTimer 루프로 프레임 처리 파이프라인 구축
- 프레임 처리 파이프라인:
  ```python
  1. 카메라 캡처: cv2.VideoCapture로 프레임 가져오기
  2. AI 추론: RVM 모델로 배경 제거 (BGRA 반환)
  3. 그린 배경 합성: 메인 윈도우용 크로마키 프리뷰 생성
  4. Qt 렌더링: QImage/QPixmap 변환 후 QLabel에 표시
  ```

### 2. Qt 환경에서의 멀티스레딩

**문제**: 메인 스레드에서 무거운 작업(AI 모델 로딩, 카메라 감지)을 수행하여 프로그램 초기 실행이 굉장히 늦고, 카메라 준비 상태까지 장기간 대기해야 함.

**발생 이유**: PyQt6의 GUI는 단일 스레드로 동작합니다. 이벤트 루프 특성 상 메인 스레드에서 UI 렌더링, 버튼 클릭 등 GUI 작업을 처리합니다. 만약 AI로딩처럼 무거운 작업을 메인 스레드가 담당하게 되면 UI업데이트가 멈추는 문제가 발생합니다.

**해결**:

- QThread 기반 워커 구현
- pyqtSignal을 통한 스레드 간 통신

AI로딩 작업, 카메라 탐지 작업을 GUI와 별도 스레드로 분리하여, UI는 즉시 표시하고 무거운 작업은 백그라운드에서 처리합니다.

## 성능 개선 경험

### 최종 시작 시간 최적화 (8.9s → 6.9s)

#### 초기 상태

1. AI 모델 로드: +6초
2. 프로그램 UI 표시
3. 카메라 감지: +3초

- 프로그램 초기 실행은 물론 준비까지 굉장히 긴 시간이 걸림
- 순차 실행으로 프로그램 실행 준비까지 총 ~8.9초

#### 개선 전략

1. **Lazy Loading 도입**

   - 모듈 임포트 시점 지연 (`torch`, `RobustVideoMatting`)
   - AI 사용 시점에 모델 로딩

   1. 프로그램 UI 표시
   2. 카메라 탐지 +3초
   3. 사용자가 카메라 동작 시 AI모델 로드 +6초

   - 프로그램 자체는 즉각 표시되나, 실질적으로 총 준비 시간은 개선되지 않음
   - 빠른 프로그램 표시로 UX개선

2. **멀티스레딩 병렬화**

   ```python
   # ModelLoadWorker: AI 모델 백그라운드 로딩
   # CameraDetectWorker: 카메라 감지 백그라운드 처리
   ```

   - 두 작업을 병렬로 실행
   - pyqtSignal로 완료 시점 동기화

   1. 프로그램 UI 표시
   2. 카메라 탐지 3초 + AI모델 로드 6초 = 6초

#### 최종 결과

- **배경 제거 기능 준비 시간**: 8.9s → 6.9s (**2초 단축, 22% 개선**)
- **UI 표시**: 8.9s → 1.4초 이내 (**7초 단축, 84% 개선**)
