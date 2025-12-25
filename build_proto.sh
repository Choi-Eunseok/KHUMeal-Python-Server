#!/bin/sh
# proto 컴파일과 import 자동수정까지 한 번에 실행
PROTO_DIR="$(dirname "$0")/proto"
PROTO_FILE="$PROTO_DIR/menu.proto"

echo "[protoc 컴파일]"
python -m grpc_tools.protoc -I"$PROTO_DIR" --python_out="$PROTO_DIR" --grpc_python_out="$PROTO_DIR" "$PROTO_FILE"

echo "[import 자동수정]"
for f in "$PROTO_DIR"/*_pb2_grpc.py; do
  if grep -q '^import menu_pb2 as menu__pb2' "$f"; then
    sed -i '' 's/^import menu_pb2 as menu__pb2/from . import menu_pb2 as menu__pb2/' "$f"
    echo "[수정됨] $(basename "$f")"
  else
    echo "[변경 없음] $(basename "$f")"

  fi
done
