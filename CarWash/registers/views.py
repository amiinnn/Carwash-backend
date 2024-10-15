from rest_framework import status,viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AdminProfile,Product,PositionQueue,UserProfile ,Car ,Workers,Position,Service,Order,OrderItem,ProductOrder,ProductOrderItem,DiscountCode
from .serializers import ProductOrderSerializer,ProductOrderItemSerializer,ProductSerializer,PositionQueueSerializer1,WorkerSerializer1,PositionQueueSerializer,DiscountCodeSerializer, OrderCreateSerializer,UserProfileSerializer, LoginSerializer ,CarSerializer,WorkersSerializer,PositionSerializer,ServiceSerializer,OrderSerializer,CarSerializer1
from django.utils import timezone 
from datetime import datetime, timedelta
from django.http import Http404
from decimal import Decimal
from django.contrib.auth.hashers import check_password
#//////////////////////////////////////////////////////////
class MyAPIView(APIView):
    allowed_methods = ['GET', 'POST','PUT','DELETE']
#//////////////////////////////////////////////////////////

class GetUserAPIView(APIView):
    def get(self, request, user_id, format=None):
        try:
            user = UserProfile.objects.get(id=user_id)
            serializer = UserProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SignupAPIView(APIView):
    def post(self, request, format=None):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            user_profile = serializer.save()
            user_data = {
                'id': user_profile.id,
                'FirstName': user_profile.Firstname,
                'LastName': user_profile.Lastname,
                'Email': user_profile.Email,
                'phoneNumber': user_profile.phoneNumber,
                'credit': user_profile.credit,
            }
            return Response(user_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            national_code = serializer.validated_data.get('nationalCode')
            password = serializer.validated_data.get('password')
            try:
                user_profile = UserProfile.objects.get(nationalCode=national_code)
                if check_password(password, user_profile.password):
                    user_data = {
                        'id': user_profile.id,
                        'FirstName': user_profile.Firstname,
                        'LastName': user_profile.Lastname,
                        'Email': user_profile.Email,
                        'phoneNumber': user_profile.phoneNumber,
                        'nationalCode':user_profile.nationalCode,
                        'credit': user_profile.credit
                    }
                    return Response(user_data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Incorrect password'}, status=status.HTTP_401_UNAUTHORIZED)
            except UserProfile.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAdminAPIView(APIView):
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            national_code = serializer.validated_data.get('nationalCode')
            password = serializer.validated_data.get('password')
            try:
                user = AdminProfile.objects.get(nationalCode=national_code, password=password)
                user_data = {
                    'FirstName': user.Firstname,
                    'LastName': user.Lastname
                }
                return Response(user_data, status=status.HTTP_200_OK)
            except AdminProfile.DoesNotExist:
                return Response({'error': 'Username or password does not exist'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileUpdateAPIView(APIView):
    def get_object(self, user_id):
        try:
            return UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            raise Http404
    def put(self, request, user_id, format=None):
        user = self.get_object(user_id)
        data = request.data.copy()
        # Remove 'nationalCode' from the data if it's present
        data.pop('nationalCode', None)
        serializer = UserProfileSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#CAR
class CarAPIView(APIView):
    def post(self, request, format=None):
        serializer = CarSerializer1(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserCarsAPIView(APIView):
    def get(self, request, user_id, format=None):
        try:
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        cars = Car.objects.filter(user=user)
        serializer =CarSerializer(cars , many=True)
        cardata={"response":serializer.data}
        return Response(cardata, status=status.HTTP_200_OK)

class CarDetailAPIView(APIView):
    def get_object(self, car_id,user_id):
        try:
            return Car.objects.get(id=car_id,user_id=user_id)
        except Car.DoesNotExist:
            raise Http404
    def get(self, request,car_id,format=None):
        user_id=request.query_params.get('user_is')
        if not user_id:
            return Response({'errer:User ID is required'},status=status.HTTP_400_BAD)
        car=self.get_object(car_id,user_id)
        serializer=CarSerializer(car)
        return Response(serializer.data)
    def put(self, request, car_id, format=None):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        car=self.get_object(car_id,user_id)
        serializer=CarSerializer(car,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, car_id, format=None):
        user_id=request.data.get('user_id')
        if not user_id:
            return Response({'error': 'User ID is requerd'},status=status.HTTP_400_BAD_REQUEST)
        car = self.get_object(car_id,request.user)
        car.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
#////////////////////////////////////////////////////////////////////////////////////////////////


#Positions
class PositionSetupAPIView(APIView):
    def post(self, request, format=None):
        positions = request.data.get('positions')  # Expecting a list of {'name': str, 'worker_id': int}
        if not positions:
            return Response({'error': 'No positions provided.'}, status=status.HTTP_400_BAD_REQUEST)
        for pos in positions:
            worker_id = pos.get('worker_id')
            name = pos.get('name')
            if not worker_id or not name:
                return Response({'error': 'Position name and worker ID are required.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                worker = Workers.objects.get(id=worker_id)
            except Workers.DoesNotExist:
                return Response({'error': f'Worker with id {worker_id} not found.'}, status=status.HTTP_404_NOT_FOUND)
            Position.objects.create(name=name, worker=worker, carStatus="Empty", status=True, freeTime=timezone.now())
        return Response({'message': 'Positions created successfully'}, status=status.HTTP_200_OK)

class PositionAPIView(APIView):
    def get(self, request, format=None):
        positions = Position.objects.all()
        response_data = []
        for position in positions:
            next_free_time = position.freeTime.strftime("%H:%M:%S") if position.freeTime else None
            # Serialize the worker object
            worker_serializer = WorkerSerializer1(position.worker)
            position_data = {
                "id": position.id,
                'name': position.name,
                'status': position.status,
                'capacity': position.capacity,  
                'next_free_time': next_free_time,
                'worker': worker_serializer.data
            }
            response_data.append(position_data)
        custom_response = {
            'response': response_data
        }
        return Response(custom_response, status=status.HTTP_200_OK)


class AssignCarToPositionAPIView(APIView):
    def put(self, request, format=None):
        position_id = request.data.get('position_id')
        car_id = request.data.get('car_id')
        if not position_id or not car_id:
            return Response({'message': 'Position ID and Car ID must be provided.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            position = Position.objects.get(id=position_id, status=True)
            car = Car.objects.get(id=car_id)
            
            queue_size = PositionQueue.objects.filter(position=position).count()
            if queue_size >= position.queue_capacity:
                return Response({'message': 'Queue is full'}, status=status.HTTP_400_BAD_REQUEST)
            
            PositionQueue.objects.create(position=position, car=car)
            
            while position.capacity > 0:
                next_in_queue = PositionQueue.objects.filter(position=position).first()
                if not next_in_queue:
                    break
                
                position.carId = next_in_queue.car
                position.carStatus = "Assigned"
                position.freeTime = timezone.now() + timedelta(hours=1)
                position.save()
                
                # Remove the car from the queue after assigning
                next_in_queue.delete()
                
                # position.capacity -= 1
                if position.capacity == 0:
                    position.status = False
                position.save()
            return Response({'message': 'Car assigned successfully', 'position': PositionSerializer(position).data}, status=status.HTTP_200_OK)
        except Position.DoesNotExist:
            return Response({'message': 'Position not found or not available'}, status=status.HTTP_404_NOT_FOUND)
        except Car.DoesNotExist:
            return Response({'message': 'Car not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        services = serializer.data
        custom_response = {
            "services": []
        }
        for service in services:
            custom_response["services"].append({
                "id": service['id'],
                "name": service['name'],
                "price": service['price'],
            })
        return Response(custom_response, status=status.HTTP_200_OK)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = serializer.save()
        except UserProfile.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Car.DoesNotExist:
            return Response({'error': 'Car not found'}, status=status.HTTP_404_NOT_FOUND)
        except Position.DoesNotExist:
            return Response({'error': 'Position not found or has no capacity'}, status=status.HTTP_404_NOT_FOUND)
        except Service.DoesNotExist:
            return Response({'error': 'One or more services not found'}, status=status.HTTP_404_NOT_FOUND)
        except serializer.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
class UpdateOrderDetailsAPIView(APIView):
    def put(self, request, format=None):
        order_id = request.data.get('order_id')
        totalprice = request.data.get('totalprice')
        tip = request.data.get('tip')
        tax=request.data.get('tax')
        statuspayment = request.data.get('statuspayment')
        try:
            order = Order.objects.get(id=order_id)
            if totalprice is not None:
                order.totalprice = totalprice
            if tip is not None:
                order.tip = tip
            if tax is not None:
                order.tax=tax
            if statuspayment is not True:
                order.statuspayment=statuspayment
            order.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#shop
class ProductListAPIView(APIView):
    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response({'products': serializer.data}, status=status.HTTP_200_OK)

class CreateOrderAPIView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        items = request.data.get('items')  # list of {product_id, quantity}
        try:
            user = UserProfile.objects.get(id=user_id)
            order = ProductOrder.objects.create(user=user, total_price=Decimal('0.00'))
            total_price = Decimal('0.00')
            order_items = []
            for item in items:
                product = Product.objects.get(id=item['product_id'])
                quantity = item.get('quantity', 1)  # Default to 1 if quantity is not provided
                if product.inventory < quantity:
                    return Response({'error': f'Not enough inventory for product {product.name}'}, status=status.HTTP_400_BAD_REQUEST)
                product.inventory -= quantity
                product.save()
                order_item = ProductOrderItem.objects.create(order=order, product=product, quantity=quantity)
                order_items.append(order_item)
                total_price += product.price * quantity
            order.total_price = total_price
            order.save()
            # سریالایزر با اضافه کردن آیتم‌های سفارش به شیء سفارش
            order_serialized = ProductOrderSerializer(order)
            order_data = order_serialized.data
            order_data['items'] = ProductOrderItemSerializer(order_items, many=True).data
            return Response(order_data, status=status.HTTP_201_CREATED)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdatePaymentStatusAPIView(APIView):
    def patch(self, request, order_id, format=None):
        try:
            # Retrieve the order based on the provided order_id
            order = ProductOrder.objects.get(id=order_id)
            # Get the new statuspayment value from the request data
            new_statuspayment = request.data.get('statuspayment')
            if new_statuspayment is None:
                return Response({'error': 'statuspayment value not provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Update the statuspayment value
            order.statuspayment = new_statuspayment
            order.save()

            return Response({'message': 'Payment status updated successfully'}, status=status.HTTP_200_OK)
        except ProductOrder.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ValidateDiscountCodeAPIView(APIView):
    def post(self, request, format=None):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'No discount code provided.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            discount_code = DiscountCode.objects.get(code=code)
            return Response({'discount_percent': discount_code.discount_percent}, status=status.HTTP_200_OK)
        except DiscountCode.DoesNotExist:
            return Response({'error': 'Invalid discount code.'}, status=status.HTTP_404_NOT_FOUND)

class UserOrdersAPIView(APIView):
    def get(self, request, user_id, format=None):
        try:
            # Retrieve orders for the given user
            orders = Order.objects.filter(user_id=user_id)
            if not orders.exists():
                return Response({'message': 'No orders found for this user'}, status=status.HTTP_404_NOT_FOUND)
            
            order_data = []
            for order in orders:
                order_items = order.order_items.all()
                cars = []
                services = []
                # Collecting car ids
                if order.car.firstId and order.car.firstId not in cars:
                    cars.append(order.car.firstId)
                if order.car.secondedId and order.car.secondedId not in cars:
                    cars.append(order.car.secondedId)
                if order.car.thirdId and order.car.thirdId not in cars:
                    cars.append(order.car.thirdId)
                if order.car.fourthId and order.car.fourthId not in cars:
                    cars.append(order.car.fourthId)
                # Collecting service names
                for item in order_items:
                    if item.service.name not in services:
                        services.append(item.service.name)
                position = order.position
                order_info = {
                    'order_id':order.id,
                    'position_name': position.name if position else None,
                    'workerFirstname':position.worker.Firstname,
                    'workerLastname':position.worker.Lastname,
                    'total_price': order.totalprice,
                    'position_worker_Firstname': position.worker.Firstname if position.worker else None,
                    'position_worker_Lastname': position.worker.Lastname if position.worker else None, 
                    'car_ids': cars,
                    'services_name': services,
                    'tax':order.tax,
                    'statuspyment':order.statuspayment
                }
                order_data.append(order_info)
            # Wrapping order_data in a single JSON object
            response_data = {
                'user_orders': order_data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserShopOrdersAPIView(APIView):
    def get(self, request, user_id, format=None):
        try:
            # Retrieve product orders for the given user
            product_orders = ProductOrder.objects.filter(user_id=user_id)
            if not product_orders.exists():
                return Response({'message': 'No product orders found for this user'}, status=status.HTTP_404_NOT_FOUND)
            
            user_shop_order = []
            for order in product_orders:
                order_items = ProductOrderItem.objects.filter(order=order)
                items = []
                for item in order_items:
                    items.append({
                        'product_name': item.product.name,
                        'product_price': item.product.price,
                        'quantity': item.quantity,
                    })
                order_info = {
                    'productorder_id': order.id,
                    'totalprice': order.total_price,
                    'items': items,
                }
                user_shop_order.append(order_info)
            # Wrapping user_shop_order in a single JSON object
            response_data = {
                'user_shop_order': user_shop_order
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class CarDetailView(APIView):
    def get(self, request, car_id):
        try:
            car = Car.objects.get(id=car_id)
            position = Position.objects.get(carId=car)
            order = Order.objects.filter(car=car).latest('created_at')
            service_end_time = order.created_at
            order_items = order.order_items.all()
            for item in order_items:
                service_end_time += item.service.duration
            data = {
                'car_status': position.carStatus,
                'position_name': position.name,
                'worker_name': f"{position.worker.Firstname} {position.worker.Lastname}",
                'service_end_time': service_end_time,
                'firstId': car.firstId,
                'secondedId': car.secondedId,
                'thirdId': car.thirdId,
                'fourthId': car.fourthId
            }
            
            return Response(data, status=status.HTTP_200_OK)
        except Car.DoesNotExist:
            return Response({'message': 'Car not found'}, status=status.HTTP_404_NOT_FOUND)
        except Position.DoesNotExist:
            return Response({'message': 'Position not found'}, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist:
            return Response({'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#Admin
#Workers
class WorkersAPIView(APIView):
    def post(self, request, format=None):
        serializer = WorkersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request, format=None):
        workers = Workers.objects.all()
        serializer = WorkersSerializer(workers, many=True)
        return Response({'response': serializer.data}, status=status.HTTP_200_OK)

class WorkerDeleteAPIView(APIView):
    def post(self, request, format=None):
        worker_id = request.data.get('worker_id')
        if not worker_id:
            return Response({'error': 'Worker ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            worker = Workers.objects.get(id=worker_id)
        except Workers.DoesNotExist:
            return Response({'error': 'Worker not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # Delete the worker (and automatically delete related positions due to the CASCADE setting)
        worker.delete()
        return Response({'message': 'Worker deleted successfully'}, status=status.HTTP_200_OK)

class WorkerCreateAPIView(APIView):
    def post(self, request, format=None):
        try:
            new_worker = Workers.objects.create(
                Firstname=request.data.get('Firstname'),
                Lastname=request.data.get('Lastname'),
                nationalCode=request.data.get('nationalCode'),
                phoneNumber=request.data.get('phoneNumber'),
                shiftDate=request.data.get('shiftDate'),
                shiftStartTime=request.data.get('shiftStartTime'),
                shiftEndTime=request.data.get('shiftEndTime')
            )
            return Response({'message': 'Worker added successfully', 'worker_id': new_worker.id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class WorkerShiftUpdateAPIView(APIView):
    def put(self, request,worker_id, format=None):
        try:
            # Retrieve the worker
            worker = Workers.objects.get(id=worker_id)
            worker.shiftStartTime = request.data.get('shiftStartTime', worker.shiftStartTime)
            worker.shiftEndTime = request.data.get('shiftEndTime', worker.shiftEndTime)
            worker.save()
            return Response({'message': 'Worker shift updated successfully'}, status=status.HTTP_200_OK)
        except Workers.DoesNotExist:
            return Response({'error': 'Worker not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AssignWorkerToPositionAPIView(APIView):
    def put(self, request, format=None):
        try:
            worker_id = request.data.get('worker_id')
            position_id = request.data.get('position_id')
            if not worker_id or not position_id:
                return Response({'error': 'Worker ID and Position ID must be provided'}, status=status.HTTP_400_BAD_REQUEST)
            worker = Workers.objects.get(id=worker_id)
            position = Position.objects.get(id=position_id)
            position.worker = worker
            position.save()
            return Response({'message': f'Worker {worker.Firstname} {worker.Lastname} assigned to position {position.name} successfully'}, status=status.HTTP_200_OK)
        except Workers.DoesNotExist:
            return Response({'error': 'Worker not found'}, status=status.HTTP_404_NOT_FOUND)
        except Position.DoesNotExist:
            return Response({'error': 'Position not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#totalprice
class AllOrdersAPIView(APIView):
    def get(self, request, format=None):
        try:
            # Retrieve all orders
            orders = Order.objects.all()
            # Serialize the orders
            serializer = OrderSerializer(orders, many=True)
            # Calculate total price
            total_price = sum(order.totalprice for order in orders)
            # Prepare the response data
            response_data = {
                'orders': serializer.data,
                'totalprice': total_price
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TotalPriceShopOrdersAPIView(APIView):
    def get(self, request, format=None):
        try:
            # Retrieve all shop orders
            shop_orders = ProductOrder.objects.all()
            # Serialize the shop orders
            shop_order_data = []
            total_price = Decimal('0.00')  # Ensure total_price is a Decimal object
            for order in shop_orders:
                order_data = {
                    'order-id': order.id,
                    'order-items': []
                }
                order_items = ProductOrderItem.objects.filter(order=order)
                for item in order_items:
                    order_item_serializer = ProductOrderItemSerializer(item)
                    order_data['order-items'].append(order_item_serializer.data)
                    # Calculate total price for the order
                    total_price += item.quantity * item.product.price
                shop_order_data.append(order_data)
            return Response({'orders': shop_order_data, 'total_price': total_price}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#users
class UserApiView(APIView):
    def get(self, request, format=None):
        try:
            users = UserProfile.objects.all()
            users_data = []
            for user in users:
                user_data = {
                    "id": user.id,
                    "Firstname": user.Firstname,
                    "Lastname": user.Lastname,
                    "Email": user.Email,
                    "phoneNumber": user.phoneNumber,
                    'nationalCode': user.nationalCode,
                    'credit': user.credit
                }
                users_data.append(user_data)
            return Response({'response': users_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateUserCreditAPIView(APIView):
    def post(self, request, format=None):
        user_id = request.data.get('user_id')
        new_credit = request.data.get('credit')
        if not user_id or not new_credit:
            return Response({'error': 'User ID and credit value are required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            user.credit = new_credit
            user.save()
            return Response({'message': 'Credit updated successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Position
class UpdatePositionAPIView(APIView):
    def patch(self, request, format=None):
        position_id = request.data.get('position_id')
        new_capacity = request.data.get('capacity')
        new_status = request.data.get('status')
        if not position_id:
            return Response({'error': 'Position ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            position = Position.objects.get(id=position_id)
        except Position.DoesNotExist:
            return Response({'error': 'Position not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            if new_capacity is not None:
                position.capacity = new_capacity
            if new_status is not None:
                position.status = new_status
            position.save()
            return Response({'message': 'Position updated successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetPositionQueueAPIView(APIView):
    def post(self, request, format=None):
        try:
            position_id = request.data.get('position_id')
            if not position_id:
                return Response({'message': 'Position ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
            position = Position.objects.get(id=position_id)
            queue = PositionQueue.objects.filter(position=position).order_by('assigned_at')
            serializer = PositionQueueSerializer1(queue, many=True)
            return Response({'queue': serializer.data}, status=status.HTTP_200_OK)
        except Position.DoesNotExist:
            return Response({'message': 'Position not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#discount
class CreateDiscountCodeAPIView(APIView):
    def post(self, request, format=None):
        serializer = DiscountCodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#Product
class CreateProductAPIView(APIView):
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#Total order
class TotalOrdersAPIView(APIView):
    def get(self, request, format=None):
        try:
            # Retrieve all orders
            orders = Order.objects.all()
            if not orders.exists():
                return Response({'message': 'No orders found'}, status=status.HTTP_404_NOT_FOUND)
            order_data = []
            for order in orders:
                order_items = order.order_items.all()
                cars = []
                services = []
                # Collecting car ids
                if order.car.firstId and order.car.firstId not in cars:
                    cars.append(order.car.firstId)
                if order.car.secondedId and order.car.secondedId not in cars:
                    cars.append(order.car.secondedId)
                if order.car.thirdId and order.car.thirdId not in cars:
                    cars.append(order.car.thirdId)
                if order.car.fourthId and order.car.fourthId not in cars:
                    cars.append(order.car.fourthId)
                # Collecting service names
                for item in order_items:
                    if item.service.name not in services:
                        services.append(item.service.name)
                position = order.position
                # Get user information
                user = order.user
                user_name = f"{user.Firstname} {user.Lastname}" if user else None
                order_info = {
                    'order_id': order.id,
                    'position_name': position.name if position else None,
                    'workerFirstname': position.worker.Firstname if position and position.worker else None,
                    'workerLastname': position.worker.Lastname if position and position.worker else None,
                    'total_price': order.totalprice, 
                    'car_ids': cars,
                    'services_name': services,
                    'tax': order.tax,
                    'statuspayment': order.statuspayment,
                    'user_name': user_name,
                    'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                order_data.append(order_info)
            # Wrapping order_data in a single JSON object
            response_data = {
                'user_orders': order_data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Total shop order
class ProductOrderListAPIView(APIView):
    def get(self, request, format=None):
        try:
            orders = ProductOrder.objects.all()
            serializer = ProductOrderSerializer(orders, many=True)
            return Response({'orders': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)