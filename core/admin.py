from django.contrib import admin

from .models import *


class PostImageAdmin(admin.StackedInline):
    model = ItemImage


@admin.register(Item)
class PostAdmin(admin.ModelAdmin):
    inlines = [PostImageAdmin]

    class Meta:
        model = Item


@admin.register(ItemImage)
class PostImageAdmin(admin.ModelAdmin):
    pass

def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'

admin.site.register(Portfolio)
admin.site.register(Partners)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Color)
