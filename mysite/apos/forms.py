from phonenumber_field.formfields import PhoneNumberField

from django import forms
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import *


class SignUpForm(UserCreationForm):
   phone_number = PhoneNumberField(help_text='Enter your phone number')

   class Meta:
      model = get_user_model()
      fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')

   def __init__(self, *args, **kwargs):
      super(SignUpForm, self).__init__(*args, **kwargs)
      self.fields['password1'].widget = forms.PasswordInput()
      self.fields['password2'].widget = forms.PasswordInput()


class LoginForm(AuthenticationForm):
   username = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
   password = forms.CharField(max_length=128, widget=forms.PasswordInput)
   phone_number = PhoneNumberField(help_text='Enter your phone number')


class DateInput(forms.DateInput):
   input_type = 'date'


class DateTimeInput(forms.DateTimeInput):
   input_type = 'datetime-local'


# Location management
class RegionLocationsForm(forms.ModelForm):
   class Meta:
      model = RegionLocations
      exclude = ['unique_identifier']


class ExternalLocationsForm(forms.ModelForm):
   class Meta:
      model = ExternalLocations
      fields = '__all__'

   def __init__(self, *args, **kwargs):
      unique_identifier = kwargs.pop('unique_identifier', None)
      super(ExternalLocationsForm, self).__init__(*args, **kwargs)

      if unique_identifier:
         related_region_locations = RegionLocations.objects.filter(unique_identifier=unique_identifier)
         self.fields['region_location'].queryset = related_region_locations


class InternalLocationsForm(forms.ModelForm):
   class Meta:
      model = InternalLocations
      exclude = ['external_location']
    

# Employee management
class EmployeesForm(forms.ModelForm):
   phone = PhoneNumberField()

   class Meta:
      model = Employees
      exclude = ['region_location', 'external_location', 'user', 'unique_identifier']
      widgets = {
         'hired_date': DateInput()
      }


class EmployeesOwnerCreateForm(forms.ModelForm):
   phone = PhoneNumberField()

   class Meta:
      model = Employees
      exclude = ['region_location', 'external_location', 'user', 'job_position']
      widgets = {
         'hired_date': DateInput()
      }


# Once the owner creates the region and external location, they will come back and add the locations to their record
class EmployeesOwnerUpdateForm(forms.ModelForm):
   phone = PhoneNumberField()

   class Meta:
      model = Employees
      exclude = ['user', 'unique_identifier', 'job_position']
      widgets = {
         'hired_date': DateInput()
      }


class RequestsCreateForm(forms.ModelForm):
   class Meta:
      model = Requests
      fields = ('request_type', 'request_message')


class RequestsResponseForm(forms.ModelForm):
    class Meta:
      model = Requests
      fields = ('request_status', 'request_response')


# Shift scheduling management
class ShiftSchedulingCreateForm(forms.ModelForm):
   class Meta:
      model = ShiftScheduling
      exclude = ['employee_swapped']
      widgets = {
         'shift_date': DateInput()
      }

   def __init__(self, *args, **kwargs):
      external_location = kwargs.pop('external_location', None)
      super(ShiftSchedulingCreateForm, self).__init__(*args, **kwargs)

      related_employees = Employees.objects.filter(external_location=external_location)
      self.fields['employee'].queryset = related_employees


class ShiftSchedulingUpdateForm(forms.ModelForm):
   class Meta:
      model = ShiftScheduling
      exclude = ['employee', 'is_open_shift']
      widgets = {
         'shift_date': DateInput()
      }
   
   def __init__(self, *args, **kwargs):
      external_location = kwargs.pop('external_location', None)
      super(ShiftSchedulingCreateForm, self).__init__(*args, **kwargs)

      related_employees = Employees.objects.filter(external_location=external_location)
      self.fields['employee_swapped'].queryset = related_employees


class DailyShiftRecordsTimeClockForm(forms.ModelForm):
   class Meta:
      model = DailyShiftRecords
      fields = ('punch_in_time', 'punch_out_time')


class BreakRecordsForm(forms.ModelForm):
   class Meta:
      model = BreakRecords
      exclude = ['employee', 'daily_shift_record']


# Inventory management
class InventoryItemsForm(forms.ModelForm):
   class Meta:
      model = InventoryItems
      exclude = ['external_location', 'par_level']      


class InventoryChecksForm(forms.ModelForm):
   class Meta:
      model = InventoryChecks
      exclude = ['employee']

   def __init__(self, *args, **kwargs):
      external_location = kwargs.pop('external_location', None)
      super(InventoryChecksForm, self).__init__(*args, **kwargs)

      related_inventory_items = InventoryItems.objects.filter(external_location=external_location)
      self.fields['inventory_item'].queryset = related_inventory_items


# Vendor management
class VendorsForm(forms.ModelForm):
   phone = PhoneNumberField()

   class Meta:
      model = Vendors
      exclude = ['external_location']


# Inventory order management
class OrdersForm(forms.ModelForm):
   class Meta:
      model = Orders
      exclude = ['external_location']
      widgets = {
         'order_date': DateInput(),
         'arrival_date': DateInput()
      }


class OrderInventoryForm(forms.ModelForm):
   class Meta:
      model = OrderInventory
      fields = '__all__'

   def __init__(self, *args, **kwargs):
      external_location = kwargs.pop('external_location', None)
      super(OrderInventoryForm, self).__init__(*args, **kwargs)

      related_orders = Orders.objects.filter(external_location=external_location)
      self.fields['order'].queryset = related_orders


# Task management
class TasksCreateForm(forms.ModelForm):
   class Meta:
      model = Tasks
      exclude = ['status', 'employee_assignor']
      widgets = {
         'due_date': DateTimeInput(format='%Y-%m-%dT%H:%M')
      }

   def __init__(self, *args, **kwargs):
      external_location = kwargs.pop('external_location', None)
      super(TasksCreateForm, self).__init__(*args, **kwargs)

      if external_location:
         related_employees = Employees.objects.filter(external_location=external_location)
         self.fields['employee_assignee'].queryset = related_employees


class TasksUpdateForm(forms.ModelForm):
   class Meta:
      model = Tasks
      exclude = ['employee_assignee', 'employee_assignor']
      widgets = {
         'due_date': DateTimeInput(format='%Y-%m-%dT%H:%M')
      }


class TaskCommentsForm(forms.ModelForm):
   class Meta:
      model = TaskComments
      exclude = ['employee_commenter']

   def __init__(self, *args, **kwargs):
      external_location = kwargs.pop('external_location', None)
      super(TaskCommentsForm, self).__init__(*args, **kwargs)

      if external_location:
         related_tasks = Tasks.objects.filter(external_location=external_location)
         self.fields['task'].queryset = related_tasks


# Recipe management
class RecipesForm(forms.ModelForm):
   class Meta:
      model = Recipes
      exclude = ['region_location']


class RecipeIngredientsForm(forms.ModelForm):
   class Meta:
      model = RecipeIngredients
      fields = '__all__'

   def __init__(self, *args, **kwargs):
      region_location = kwargs.pop('region_location', None)
      external_location = kwargs.pop('external_location', None)
      super(RecipeIngredientsForm, self).__init__(*args, **kwargs)

      if region_location and external_location:
         related_recipes = Recipes.objects.filter(region_location=region_location)
         related_inventory_items = InventoryItems.objects.filter(external_location=external_location)

         self.fields['recipe'].queryset = related_recipes
         self.fields['inventory_item'].queryset = related_inventory_items


# Menu management
class MenuItemsForm(forms.ModelForm):
   class Meta:
      model = MenuItems
      exclude = ['external_location']

   def __init__(self, *args, **kwargs):
      region_location = kwargs.pop('region_location', None)
      super(MenuItemsForm, self).__init__(*args, **kwargs)

      if region_location:
         related_recipes = Recipes.objects.filter(region_location=region_location)
         self.fields['recipe'].queryset = related_recipes


class AddOnsCreateForm(forms.ModelForm):
   class Meta:
      model = AddOns
      fields = '__all__'

   def __init__(self, *args, **kwargs):
      external_location = kwargs.pop('external_location', None)
      super(AddOnsForm, self).__init__(*args, **kwargs)

      if external_location:
         related_inventory_items = InventoryItems.objects.filter(external_location=external_location)
         self.fields['inventory_item'].queryset = related_inventory_items


class AddOnsUpdateForm(forms.ModelForm):
   class Meta:
      model = AddOns
      exclude = ['inventory_item']


class MenuItemAddOnsForm(forms.ModelForm):
   class Meta:
      model = MenuItemAddOns
      fields = '__all__'

   def __init__(self, *args, **kwargs):
      external_location = kwargs.pop('external_location', None)
      super(MenuItemAddOnsForm, self).__init__(*args, **kwargs)

      if external_location:
         related_menu_items = MenuItems.objects.filter(external_location=external_location)
         related_add_ons = AddOns.objects.filter(external_location=external_location)

         self.fields['menu_item'].queryset = related_menu_items
         self.fields['add_on'].queryset = related_add_ons


class MenuItemOrdersCreateForm(forms.ModelForm):
   add_ons = forms.ModelMultipleChoiceField(
      queryset=AddOns.objects.none(),
      widget=forms.CheckboxSelectMultiple,
      required=False
   )

   class Meta:
      model = MenuItemOrders
      fields = ('add_ons', 'quantity', 'internal_location')

   def __init__(self, *args, **kwargs):
      menu_item = kwargs.pop('menu_item', None)
      super(MenuItemOrdersCreateForm, self).__init__(*args, **kwargs)

      if menu_item:
         related_add_ons = AddOns.objects.filter(
            id__in=MenuItemAddOns.objects.filter(
               menu_item=menu_item
            ).values_list('add_on', flat=True)
         )

         self.fields['add_ons'].queryset = related_add_ons


class MenuItemOrdersUpdateForm(forms.ModelForm):
   class Meta:
      model = MenuItemOrders
      fields = ('order_status',)


# Menu waste management
class WasteRecordsForm(forms.ModelForm):
   class Meta:
      model = WasteRecords
      fields = '__all__'

   def __init__(self, *args, **kwargs):
      externalt_location = kwargs.pop('external_location', None)
      super(WasteRecordsForm, self).__init__(*args, **kwargs)

      if external_location:
         related_menu_items = MenuItems.objects.filter(external_location=external_location)
         self.fields['menu_item'].queryset = related_menu_items


# Receipt creator + transactions log/tracker
class PaymentsForm(forms.ModelForm):
   class Meta:
      model = Payments
      exclude = ['employee']

   def __init__(self, *args, **kwargs):
      external_location = kwargs.pop('external_location', None)
      super(PaymentsForm, self).__init__(*args, **kwargs)
      
      if external_location:
         related_internal_locations = InternalLocations.objects.filter(external_location=external_location)
         self.fields['internal_location'].queryset = related_internal_locations


# Nutrition and allergen management
class NutritionAllergenInfoCreateForm(forms.ModelForm):
   class Meta:
      model = NutritionAllergenInfo
      fields = '__all__'

   def __init__(self, *args, **kwargs):
      external_location = kwargs.pop('external_location', None)
      super(NutritionAllergenInfoCreateForm, self).__init__(*args, **kwargs)

      if external_location:
         related_menu_items = MenuItems.objects.filter(external_location=external_location)
         self.fields['menu_item'].queryset = related_menu_items


class NutritionAllergenInfoUpdateForm(forms.ModelForm):
   class Meta:
      model = NutritionAllergenInfo
      exclude = ['menu_item']


# Inventory cost reports
class AccountingPeriodsForm(forms.ModelForm):
   class Meta:
      model = AccountingPeriods
      exclude = ['region_location']
      widgets = {
         'accounting_period_start': DateInput(),
         'accounting_period_end': DateInput()
      }


class InventoryTransfersForm(forms.ModelForm):
   class Meta:
      model = InventoryTransfers
      fields = '__all__'
   
   def __init__(self, *args, **kwargs):
      region_location = kwargs.pop('region_location', None)
      external_location = kwargs.pop('external_location', None)
      super(InventoryTransfersForm, self).__init__(*args, **kwargs)

      if region_location and external_location:
         related_external_locations = ExternalLocations.objects.filter(region_location=region_location)
         related_inventory_items = InventoryItems.objects.filter(external_location=external_location)

         self.fields['source_external_location'].queryset = related_external_locations
         self.fields['destination_external_location'].queryset = related_external_locations
         self.fields['inventory_item'].queryset = related_inventory_items


class InventoryTransfersInternalForm(forms.ModelForm):
   class Meta:
      model = InventoryTransfersInternal
      fields = ('source_external_location', 'destination_external_location')

   def __init__(self, *args, **kwargs):
      inventory_transfer = kwargs.pop('inventory_transfer', None)
      super(InventoryTransfersInternalForm, self).__init__(*args, **kwargs)
      
      if inventory_transfer:
         related_inventory_transfer = InventoryTransfers.objects.get(pk=inventory_transfer)

         self.fields['source_internal_location'].queryset = InternalLocations.objects.filter(
            external_location=related_inventory_transfer.source_external_location
         )
         self.fields['destination_internal_location'].queryset = InternalLocations.objects.filter(
            external_location=related_inventory_transfer.destination_external_location
         )


class InventoryWasteBinForm(forms.ModelForm):
   class Meta:
      model = InventoryWasteBin
      exclude = ['employee_reporter']

   def __init__(self, *args, **kwargs):
      external_location = kwargs.pop('external_location', None)
      super(InventoryWasteBinForm, self).__init__(*args, **kwargs)

      if external_location:
         related_inventory_items = InventoryItems.objects.filter(external_location=external_location)
         related_employees = Employees.objects.filter(external_location=external_location)

         self.fields['inventory_item'] = related_inventory_items
         self.fields['employee_culprit'] = related_employees


# Tip management
class EmployeeTipRecordsForm(forms.ModelForm):
   class Meta:
      model = EmployeeTipRecords
      exclude = ['external_location', 'employee', 'daily_shift_record']

   def __init__(self, *args, **kwargs):
      external_location = kwargs.pop('external_location', None)
      super(EmployeeTipRecordsForm, self).__init__(*args, **kwargs)

      if external_location:
         related_internal_locations = InternalLocations.objects.filter(external_location=external_location)
         self.fields['internal_location'].queryset = related_internal_locations


class TipPoolingRecordsForm(forms.ModelForm):
   class Meta:
      model = TipPoolingRecords
      exclude = ['external_location']
      widgets = {
         'date': DateInput()
      }
