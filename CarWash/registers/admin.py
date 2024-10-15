from django.contrib import admin
from .models import AdminProfile,PositionQueue,UserProfile, Car, Workers, Position, Service, Order, OrderItem,Product,ProductOrderItem,ProductOrder,DiscountCode,ProductOrder

class AdminProfileAdmin(admin.ModelAdmin):
    list_display=('Firstname', 'Lastname','nationalCode')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('Firstname', 'Lastname', 'Email', 'nationalCode', 'phoneNumber','id','credit')
    search_fields = ('Firstname', 'Lastname', 'Email', 'nationalCode','id')

class CarAdmin(admin.ModelAdmin):
    list_display = ('user', 'model', 'color', 'firstId', 'secondedId', 'thirdId', 'fourthId','id')
    search_fields = ('user__Firstname', 'user__Lastname', 'model', 'color',)

class WorkersAdmin(admin.ModelAdmin):
    list_display = ('Firstname', 'Lastname', 'nationalCode', 'phoneNumber', 'shiftDate', 'shiftStartTime', 'shiftEndTime',"id")
    search_fields = ('Firstname', 'Lastname', 'nationalCode', 'phoneNumber')

class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'carStatus', 'worker', 'freeTime','id')
    search_fields = ('name', 'carStatus', 'worker__Firstname', 'worker__Lastname')

class PositionQueueAdmin(admin.ModelAdmin):
    list_display = ('position','car','assigned_at','id')    
    
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration','id')
    search_fields = ('name','price','duration','id')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at','id', 'totalprice', 'tip','tax','statuspayment']
    search_fields = ('user__Firstname', 'user__Lastname')
    
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'rating', 'inventory')
    search_fields = ('name', 'description')
    list_filter = ('rating', 'price')
    ordering = ('name',)

class ProductOrderItemInline(admin.TabularInline):
    model = ProductOrderItem
    extra = 1

class ProductOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'created_at')
    search_fields = ('user__user__username',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    inlines = [ProductOrderItemInline]


class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('code','discount_percent','id')
    


admin.site.register(PositionQueue,PositionQueueAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Position,PositionAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Car,CarAdmin)
admin.site.register(Workers,WorkersAdmin)
admin.site.register(AdminProfile,AdminProfileAdmin)
admin.site.register(DiscountCode,DiscountCodeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductOrder, ProductOrderAdmin)
admin.site.register(ProductOrderItem)



