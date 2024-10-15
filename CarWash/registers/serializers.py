from rest_framework import serializers
from .models import AdminProfile,Product,UserProfile,Car,Workers,Position,Service, Order, OrderItem,ProductOrderItem,ProductOrder,DiscountCode,PositionQueue
from datetime import timedelta
from django.utils import timezone
#car
class CarSerializer(serializers.ModelSerializer):
    user_firstname = serializers.CharField(source='user.Firstname')
    user_lastname = serializers.CharField(source='user.Lastname')
    user_nationalcode = serializers.CharField(source='user.nationalCode')
    user_phonenumber = serializers.CharField(source='user.phoneNumber')

    class Meta:
        model = Car
        fields = ['id', 'user_firstname', 'user_lastname', 'user_nationalcode', 'user_phonenumber', 'model', 'color', 'firstId', 'secondedId', 'thirdId', 'fourthId']

class CarSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = "__all__"




#user
class LoginSerializer(serializers.Serializer):
    nationalCode = serializers.CharField(max_length=10)
    password = serializers.CharField(max_length=16)
    
class UserProfileSerializer(serializers.ModelSerializer):
    nationalCode = serializers.CharField(max_length=10, write_only=True)  # Add nationalCode field
    
    class Meta:
        model = UserProfile
        fields = ['id', 'Firstname', 'Lastname', 'Email', 'nationalCode', 'phoneNumber', 'password','credit']
        extra_kwargs = {'password': {'write_only': True}}  # Hide passwords in response

    def validate_nationalCode(self, value):
        if UserProfile.objects.filter(nationalCode=value).exists():
            raise serializers.ValidationError("This national code is already taken.")
        return value
    
    def create(self, validated_data):
        validated_data.pop('passwordConfirmation', None)  # Remove password confirmation from validated data
        return UserProfile.objects.create(**validated_data)

class UserProfileSerializer1(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['Firstname', 'Lastname', 'nationalCode', 'phoneNumber']

class ProductOrderSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer1()

    class Meta:
        model = ProductOrder
        fields = ['id', 'user', 'total_price', 'created_at', 'statuspayment']
#workers
class WorkersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workers
        fields = ['id', 'Firstname', 'Lastname', 'nationalCode', 'phoneNumber', 'shiftDate', 'shiftStartTime', 'shiftEndTime']

    def validate(self, data):
        if data['shiftStartTime'] >= data['shiftEndTime']:
            raise serializers.ValidationError("Shift start time must be before end time.")
        return data
    
class WorkerSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Workers
        fields = ['id', 'Firstname', 'Lastname']
    
#Position
class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'
        
class PositionSerializer(serializers.ModelSerializer):
    freeTime = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = ['id', 'name', 'status', 'queue_capacity', 'capacity', 'carId', 'carStatus', 'freeTime']

    def get_freeTime(self, obj):
        if obj.freeTime:
            return obj.freeTime.strftime('%Y-%m-%d %H:%M:%S %Z')
        return None

class PositionQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositionQueue
        fields = '__all__'

class PositionQueueSerializer1(serializers.ModelSerializer):
    car = CarSerializer(read_only=True)
    user_nationalCode = serializers.SerializerMethodField()

    class Meta:
        model = PositionQueue
        fields = ['car', 'user_nationalCode']

    def get_user_nationalCode(self, obj):
        return obj.car.user.nationalCode if obj.car.user else None

#servises
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['service', 'quantity']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem  # Assuming OrderItem is the correct model for services
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    services = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'worker', 'car', 'position', 'services', 'created_at']
        

class OrderCreateSerializer(serializers.ModelSerializer):
    service_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    position_id = serializers.IntegerField()
    car_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Order
        fields = ['position_id', 'car_id', 'user_id', 'service_ids']

    def create(self, validated_data):
        position_id = validated_data.pop('position_id')
        car_id = validated_data.pop('car_id')
        user_id = validated_data.pop('user_id')
        service_ids = validated_data.pop('service_ids')
        
        # Fetch related objects
        user = UserProfile.objects.get(id=user_id)
        car = Car.objects.get(id=car_id, user=user)
        position = Position.objects.get(id=position_id, status=True)
        
        # Check position capacity
        if position.capacity <= 0:
            raise serializers.ValidationError("Position has no capacity left")
        
        # Create order
        order = Order.objects.create(user=user, car=car, position=position)
        
        # Calculate total duration and create order items
        total_duration = timedelta()
        for service_id in service_ids:
            service = Service.objects.get(id=service_id)
            OrderItem.objects.create(order=order, service=service, quantity=1)
            total_duration += service.duration
        
        # Update position
        position.freeTime += total_duration
        position.capacity -= 1
        if position.capacity == 0:
            position.status = False
        position.save()
        
        # Calculate total price
        order.calculate_total_price()
        return order

#shop
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'rating', 'image', 'inventory']

class ProductOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOrderItem
        fields = ['product', 'quantity']

class ProductOrderSerializer(serializers.ModelSerializer):
    items = ProductOrderItemSerializer(many=True, source='order_items')

    class Meta:
        model = ProductOrder
        fields = ['id', 'user', 'total_price', 'created_at', 'items']

class DiscountCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = ['code', 'discount_percent']