import grpc
from concurrent import futures
import time
import proto.menu_pb2
import proto.menu_pb2_grpc
from functions.find_recent_menu_post import find_recent_menu
from functions.extract_menu import parse_menu_to_structured_data

class MenuService(proto.menu_pb2_grpc.MenuServiceServicer):
    def FindRecentMenu(self, request, context):
        result = find_recent_menu(request.base_url, request.board_id, request.keyword)
        return proto.menu_pb2.FindRecentMenuResponse(
            board_id=str(result.get('board_id', '')),
            base_date=str(result.get('base_date', '')),
            image_url=result.get('image_url', ''),
            prev_board_id=str(result.get('prev_board_id', ''))
        )

    def ParseMenu(self, request, context):
        menu_list = parse_menu_to_structured_data(request.image_url)
        response = proto.menu_pb2.ParseMenuResponse()
        for menu in menu_list:
            m = response.menu.add()
            m.corner_info = menu.get('corner_info', '')
            m.day_info = menu.get('day_info', '')
            m.menu_items.extend(menu.get('menu_items', []))
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    proto.menu_pb2_grpc.add_MenuServiceServicer_to_server(MenuService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('gRPC server started on port 50051')
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
