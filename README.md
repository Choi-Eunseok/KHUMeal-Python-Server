# 메뉴 게시물 크롤링 및 메뉴 추출 gRPC 서버

## 구성
- Python 3.11
- gRPC (grpcio, grpcio-tools)
- Docker, docker-compose
- proto 기반 서비스

## 폴더 구조 예시
```
docker_test/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── build_proto.sh
├── proto/
│   ├── menu.proto
│   ├── menu_pb2.py
│   └── menu_pb2_grpc.py
├── grpc_server.py
├── functions/
│   ├── extract_menu.py
│   └── find_recent_menu_post.py
├── utils/
│   ├── utils.py
│   └── lines.py
...
```

## 빌드 및 실행 방법

### 1. proto 파일 컴파일 및 import 자동수정
```sh
sh build_proto.sh
```


### 2. Docker 이미지 빌드 및 실행
```sh
docker build -t menu-grpc .
docker run -p 50051:50051 menu-grpc
```
서버가 50051 포트로 실행됩니다.

## 개발/테스트
- 로컬에서 직접 실행: `python grpc_server.py`
- gRPC 클라이언트는 proto/menu.proto 참고

## 기타

* .gitignore에 gRPC 생성 파일, 캐시, 환경파일 등 포함

