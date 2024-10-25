import random
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import *
from .forms import *
from .mixins import *
from .utils import *


# User signup + authentication
class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('verify_signup')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        phone_number = form.cleaned_data['phone_number']
        user.save()

        verification_code = send_verification_code(phone_number)

        self.request.session['verification_code'] = verification_code
        self.request.session['phone_number'] = phone_number

        return super().form_valid(form)


class VerifySignUpView(FormView):
    template_name = 'registration/verify_signup.html'

    def post(self, request, *args, **kwargs):
        code = request.POST.get('code')
        stored_code = request.session.get('verification_code')

        if code == str(stored_code):
            phone_number = request.session.get('phone_number')
            user = User.objects.get(profile__phone_number=phone_number)
            login(request, user)

            return redirect('home')

        else:
            context = {'error': 'The code does not match the sent verification code'}
            return render(request, self.template_name, context)


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('verify_login')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        phone_number = form.cleaned_data['phone_number']

        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            verification_code = send_verification_code(phone_number)

            self.request.session['verification_code'] = verification_code
            self.request.session['phone_number'] = phone_number

            return super().form_valid(form)

        else:
            return self.form_invalid(form)


class VerifyLoginView(FormView):
    template_name = 'registration/verify_login.html'

    def post(self, request, *args, **kwargs):
        code = request.POST.get('code')
        stored_code = request.session.get('verification_code')

        if code == str(stored_code):
            phone_number = request.session.get('phone_number')
            user = User.objects.get(profile__phone_number=phone_number)
            login(request, user)

            return redirect('home')
        
        else:
            return render(request, self.template_name, {'error': 'The code does not match the sent verification code'})


def logout_request(request):
    logout(request)
    return redirect('login')


# Homepage
@login_required
def home(request):
    employee = Employees.objects.filter(user=request.user).first()

    if employee:
        context = {'name': employee.first_name}
    else:
        context = {'name': 'Hello there! Add yourself to \'Employees\' to get started!'}

    return render(request, 'apos/home.html', context)


# Location management
class RegionLocationsListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = RegionLocations
    template_name = 'apos/regions.html'


class RegionLocationsCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = RegionLocations
    form_class = RegionLocationsForm
    template_name = 'apos/region_create.html'
    success_url = reverse_lazy('regions')

    def form_valid(self, form):
        user = self.request.user
        unique_identifier = get_object_or_404(Employees, user=user).unique_identifier

        messages.success(self.request, f'Region {form.instance.region_name} added successfully!')
        return super().form_valid(form)


class RegionLocationsUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = RegionLocations
    form_class = RegionLocationsForm
    template_name = 'apos/region_update.html'
    success_url = reverse_lazy('regions')

    def form_valid(self, form):
        messages.success(self.request, f'Region updated successfully!')
        return super().form_valid(form)


class RegionLocationsDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = RegionLocations
    template_name = 'apos/region_delete.html'
    success_url = reverse_lazy('regions')


class ExternalLocationsListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = ExternalLocations
    template_name = 'apos/external_locations.html'


class ExternalLocationsCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = ExternalLocations
    form_class = ExternalLocationsForm
    template_name = 'apos/external_location_create.html'
    success_url = reverse_lazy('external_locations')

    def form_valid(self, form):
        messages.success(self.request, f'External location {form.instance.location_name} added successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['unique_identifier'] = employee.unique_identifier

        return kwargs


class ExternalLocationsUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = ExternalLocations
    form_class = ExternalLocationsForm
    template_name = 'apos/external_location_update.html'
    success_url = reverse_lazy('external_locations')

    def form_valid(self, form):
        messages.success(self.request, f'External location updated successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['unique_identifier'] = employee.unique_identifier

        return kwargs


class ExternalLocationsDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = ExternalLocations
    template_name = 'apos/external_location_delete.html'
    success_url = reverse_lazy('external_locations')


class InternalLocationsListView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, ListView):
    model = InternalLocations
    template_name = 'apos/internal_locations.html'


class InternalLocationsCreateView(LoginRequiredMixin, OwnerOrManagementRequiredMixin, CreateView):
    model = InternalLocations
    form_class = InternalLocationsForm
    template_name = 'apos/internal_location_create.html'
    success_url = reverse_lazy('internal_locations')

    def form_valid(self, form):
        user = self.request.user
        external_location = get_object_or_404(Employees, user=user).external_location
        form.instance.external_location = external_location

        messages.success(self.request, f'Internal location {form.instance.location_name} added successfully!')
        return super().form_valid(form)


class InternalLocationsUpdateView(LoginRequiredMixin, OwnerOrManagementRequiredMixin, UpdateView):
    model = InternalLocations
    form_class = InternalLocationsForm
    template_name = 'apos/internal_location_update.html'
    success_url = reverse_lazy('internal_locations')

    def form_valid(self, form):
        messages.success(self.request, f'Internal location updated successfully!')
        return super().form_valid(form)


class InternalLocationsDeleteView(LoginRequiredMixin, OwnerOrManagementRequiredMixin, DeleteView):
    model = InternalLocations
    template_name = 'apos/internal_location_delete.html'
    success_url = reverse_lazy('internal_locations')


class LocationTrainingInsightsListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = LocationTrainingInsights
    template_name = 'apos/location_training_insights.html'


# Employee management
class EmployeesListView(LoginRequiredMixin, OwnerOrManagementFullChefOrEmployeeLimitedPermissionMixin, ListView):
    model = Employees
    template_name = 'apos/employees.html'


class EmployeesCreateView(LoginRequiredMixin, OwnerOrManagementRequiredMixin, CreateView):
    model = Employees
    form_class = EmployeesForm
    template_name = 'apos/employee_create.html'
    success_url = reverse_lazy('employees')

    def form_valid(self, form):
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        form.instance.region_location = employee.region_location
        form.instance.external_location = employee.external_location

        messages.success(self.request, 'An employee has been created successfully. Please verify the employee details.')
        return super().form_valid(form)


class EmployeesOwnerCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = Employees
    form_class = EmployeesOwnerCreateForm
    template_name = 'apos/employee_create.html'
    success_url = reverse_lazy('employees')

    def form_valid(self, form):
        form.instance.job_position = 'Owner'
        messages.warning(self.request, 'An owner as been created successfully. Make sure that this action is intentional and not a mistake. If intentional, ignore this warning.')
        return super().form_valid(form)


class EmployeesUpdateView(LoginRequiredMixin, OwnerOrManagementRequiredMixin, UpdateView):
    model = Employees
    form_class = EmployeesForm
    template_name = 'apos/employee_update.html'
    success_url = reverse_lazy('employees')

    def form_valid(self, form):
        messages.success(self.request, 'Employee updated successfully!')
        return super().form_valid(form)


class EmployeesOwnerUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Employees
    form_class = EmployeesOwnerUpdateForm
    template_name = 'apos/employee_update.html'
    success_url = reverse_lazy('employees')

    def form_valid(self, form):
        messages.warning(self.request, 'Owner updated successfully. Make sure that this action is intentional and not a mistake. If intentional, ignore this warning.')
        return super().form_valid(form)


class EmployeesDeleteView(LoginRequiredMixin, OwnerOrManagementRequiredMixin, DeleteView):
    model = Employees
    template_name = 'apos/employee_delete.html'
    success_url = reverse_lazy('employees')


class EmployeesPerformanceListView(LoginRequiredMixin, OwnerOrManagementFullChefOrEmployeeLimitedPermissionMixin, ListView):
    model = EmployeesPerformance
    template_name = 'apos/employees_performance.html'


class RequestsListView(LoginRequiredMixin, OwnerOrManagementOrChefFullEmployeeLimitedPermissionMixin, ListView):
    model = Requests
    template_name = 'apos/requests.html'


class RequestsCreateView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, CreateView):
    model = Requests
    form_class = RequestsCreateForm
    template_name = 'apos/request_create.html'
    success_url = reverse_lazy('requests')

    def form_valid(self, form):
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        form.instance.employee_requestor = employee

        messages.success(self.request, 'Request successfully created!')
        return super().form_valid(form)


class RequestsUpdateView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, UpdateView):
    model = Requests
    form_class = RequestsResponseForm
    template_name = 'apos/request_update.html'
    success_url = reverse_lazy('requests')

    def form_valid(self, form):
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        form.instance.employee_responder = employee
        
        messages.success(self.request, 'Request successfully updated!')
        return super().form_valid(form)


class RequestsDeleteView(LoginRequiredMixin, AllGroupsUserLocationFilteredMixin, DeleteView):
    model = Requests
    template_name = 'apos/request_delete.html'
    success_url = reverse_lazy('requests')


# Shift scheduling management
class ShiftSchedulingListView(LoginRequiredMixin, OwnerOrManagementOrChefFullEmployeeLimitedPermissionMixin, ListView):
    model = ShiftScheduling
    template_name = 'apos/shift_scheduling.html'


class ShiftSchedulingCreateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, CreateView):
    model = ShiftScheduling
    form_class = ShiftSchedulingCreateForm
    template_name = 'apos/shift_scheduling_create.html'
    success_url = reverse_lazy('shift_scheduling')

    def form_valid(self, form):
        if form.instance.employee and form.instance.is_open_shift:
            form.add_error(None, 'You cannot create an open shift for an employee!')
            return self.form_invalid(form)
        
        if form.instance.employee:
            messages.success(self.request, f'Shift for {form.instance.employee.first_name} successfully created!')
        else:
            messages.success(self.request, 'Open shift successfully created!')

        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['external_location'] = external_location

        return kwargs


class ShiftSchedulingUpdateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, UpdateView):
    model = ShiftScheduling
    form_class = ShiftSchedulingUpdateForm
    template_name = 'apos/shift_scheduling_update.html'
    success_url = reverse_lazy('shift_scheduling')

    def form_valid(self, form):
        messages.success(self.request, f'Shift for {form.instance.employee.first_name} successfully updated!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['external_location'] = external_location

        return kwargs


class ShiftSchedulingDeleteView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, DeleteView):
    model = ShiftScheduling
    template_name = 'apos/shift_scheduling_delete.html'
    success_url = reverse_lazy('shift_scheduling')


class DailyShiftRecordsListView(LoginRequiredMixin, OwnerOrManagementOrChefFullEmployeeLimitedPermissionMixin, ListView):
    model = DailyShiftRecords
    template_name = 'apos/daily_shift_records.html'


class DailyShiftRecordsUpdateView(LoginRequiredMixin, AllGroupsUserLocationFilteredMixin, UpdateView):
    model = DailyShiftRecords
    form_class = DailyShiftRecordsTimeClockForm
    template_name = 'apos/daily_shift_record_update.html'
    success_url = reverse_lazy('daily_shift_records')


class WeeklyShiftRecordsListView(LoginRequiredMixin, OwnerOrManagementOrChefFullEmployeeLimitedPermissionMixin, ListView):
    model = WeeklyShiftRecords
    template_name = 'apos/weekly_shift_records.html'


class BreakRecordsListView(LoginRequiredMixin, OwnerOrManagementOrChefFullEmployeeLimitedPermissionMixin, ListView):
    model = BreakRecords
    template_name = 'apos/break_records.html'


class BreakRecordsCreateView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, CreateView):
    model = BreakRecords
    form_class = BreakRecordsForm
    template_name = 'apos/break_record_create.html'
    success_url = reverse_lazy('break_records')

    def form_valid(self, form):
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        form.instance.employee = employee
        form.instance.daily_shift_record = DailyShiftRecords.objects.filter(
            external_location=employee.external_location,
            employee=employee,
            shift_date=date.today(),
            punch_in_time__isnull=False,
            punch_out_time__isnull=True
         ).pk

        messages.success(self.request, f'Dear {employee.first_name}, remember to not go over your intended break time!')
        return super().form_valid(form)


class BreakRecordsUpdateView(LoginRequiredMixin, AllGroupsUserLocationFilteredMixin, UpdateView):
    model = BreakRecords
    form_class = BreakRecordsForm
    template_name = 'apos/break_record_update.html'
    success_url = reverse_lazy('break_records')

    def form_valid(self, form):
        messages.success(self.request, 'Break record successfully updated!')
        return super().form_valid(form)


# Inventory management
class InventoryItemsListView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, ListView):
    model = InventoryItems
    template_name = 'apos/inventory_items.html'


class InventoryItemsCreateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, CreateView):
    model = InventoryItems
    form_class = InventoryItemsForm
    template_name = 'apos/inventory_item_create.html'
    success_url = reverse_lazy('inventory_items')

    def form_valid(self, form):
        user = self.request.user
        external_location = get_object_or_404(Employees, user=user).external_location
        form.instance.external_location = external_location

        messages.success(self.request, f'Inventory item called \'{form.instance.item_name}\' successfully created!')
        return super().form_valid(form)


class InventoryItemsUpdateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, UpdateView):
    model = InventoryItems
    form_class = InventoryItemsForm
    template_name = 'apos/inventory_item_update.html'
    success_url = reverse_lazy('inventory_items')

    def form_valid(self, form):
        messages.success(self.request, 'Inventory item successfully updated!')
        return super().form_valid(form)


class InventoryItemsDeleteView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, DeleteView):
    model = InventoryItems
    template_name = 'apos/inventory_item_delete.html'
    success_url = reverse_lazy('inventory_items')


class InventoryChecksListView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, ListView):
    model = InventoryChecks
    template_name = 'apos/inventory_checks.html'


class InventoryChecksCreateView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, CreateView):
    model = InventoryChecks
    form_class = InventoryChecksForm
    template_name = 'apos/inventory_check_create.html'
    success_url = reverse_lazy('inventory_checks')

    def form_valid(self, form):
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        form.instance.employee = employee

        messages.success(self.request, f'Inventory check for {form.instance.item.item_name} successfully logged!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['external_location'] = employee.external_location

        return kwargs


class InventoryChecksUpdateView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, UpdateView):
    model = InventoryChecks
    form_class = InventoryChecksForm
    template_name = 'apos/inventory_check_update.html'
    success_url = reverse_lazy('inventory_checks')

    def form_valid(self, form):
        messages.success(self.request, 'Inventory check successfully updated!')
        return super().form_valid(form)


class InventoryChecksDeleteView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, DeleteView):
    model = InventoryChecks
    template_name = 'apos/inventory_check_delete.html'
    success_url = reverse_lazy('inventory_checks')


# Vendor management
class VendorsListView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, ListView):
    model = Vendors
    template_name = 'apos/vendors.html'


class VendorsCreateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, CreateView):
    model = Vendors
    form_class = VendorsForm
    template_name = 'apos/vendor_create.html'
    success_url = reverse_lazy('vendors')

    def form_valid(self, form):
        user = self.request.user
        external_location = get_object_or_404(Employees, user=user).external_location
        form.instance.external_location = external_location

        messages.success(self.request, f'Vendor \'{form.instance.vendor_name}\' successfully added!')
        return super().form_valid(form)


class VendorsUpdateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, UpdateView):
    model = Vendors
    form_class = VendorsForm
    template_name = 'apos/vendor_update.html'
    success_url = reverse_lazy('vendors')

    def form_valid(self, form):
        messages.success(self.request, 'Vendor successfully updated!')
        return super().form_valid(form)


class VendorsDeleteView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, DeleteView):
    model = Vendors
    template_name = 'apos/vendor_delete.html'
    success_url = reverse_lazy('vendors')


# Inventory order management
class OrdersListView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, ListView):
    model = Orders
    template_name = 'apos/orders.html'


class OrdersCreateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, CreateView):
    model = Orders
    form_class = OrdersForm
    template_name = 'apos/order_create.html'
    success_url = reverse_lazy('orders')

    def form_valid(self, form):
        user = self.request.user
        external_location = get_object_or_404(Employees, user=user).external_location
        form.instance.external_location = external_location

        messages.success(self.request, f'Order successfully added!')
        return super().form_valid(form)


class OrdersUpdateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, UpdateView):
    model = Orders
    form_class = OrdersForm
    template_name = 'apos/order_update.html'
    success_url = reverse_lazy('orders')

    def form_valid(self, form):
        messages.success(self.request, 'Order successfully updated!')
        return super().form_valid(form)


class OrderInventoryListView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, ListView):
    model = OrderInventory
    template_name = 'apos/order_inventory.html'


class OrderInventoryCreateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, CreateView):
    model = OrderInventory
    form_class = OrderInventoryForm
    template_name = 'apos/order_inventory_create.html'
    success_url = reverse_lazy('order_inventory')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['external_location'] = employee.external_location

        return kwargs


class OrderInventoryUpdateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, UpdateView):
    model = OrderInventory
    form_class = OrderInventoryForm
    template_name = 'apos/order_inventory_update.html'
    success_url = reverse_lazy('order_inventory')

    def form_valid(self, form):
        messages.success(self.request, 'Order inventory successfully updated!')
        return super().form_valid(form)


class OrderInventoryAlertsListView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, ListView):
    model = OrderInventoryAlerts
    template_name = 'apos/order_inventory_alerts.html'

    def form_valid(self, form):
        messages.success(self.request, 'You have a new alert!')
        return super().form_valid(form)


# Task management
class TasksListView(LoginRequiredMixin, OwnerOrManagementOrChefFullEmployeeLimitedPermissionMixin, ListView):
    model = Tasks
    template_name = 'apos/tasks.html'


class TasksCreateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, CreateView):
    model = Tasks
    form_class = TasksCreateForm
    template_name = 'apos/task_create.html'
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        form.instance.employee_assignor = employee
        
        messages.success(self.request, f'Task \'{form.instance.task_name}\' successfully assigned!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['external_location'] = employee.external_location

        return kwargs


class TasksUpdateView(LoginRequiredMixin, AllGroupsUserLocationFilteredMixin, UpdateView):
    model = Tasks
    form_class = TasksUpdateForm
    template_name = 'apos/task_update.html'
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        messages.success(self.request, 'Task successfully updated!')
        return super().form_valid(form)


class TasksDeleteView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, DeleteView):
    model = Tasks
    template_name = 'apos/task_delete.html'
    success_url = reverse_lazy('tasks')


class TaskCommentsListView(LoginRequiredMixin, OwnerOrManagementOrChefFullEmployeeLimitedPermissionMixin, ListView):
    model = TaskComments
    template_name = 'apos/task_comments.html'


class TaskCommentsCreateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, CreateView):
    model = TaskComments
    form_class = TaskCommentsForm
    template_name = 'apos/task_comment_create.html'
    success_url = reverse_lazy('task_comments')

    def form_valid(self, form):
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        form.instance.employee_commenter = employee

        messages.success(self.request, f'Comment added!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['external_location'] = employee.external_location

        return kwargs


class TaskCommentsUpdateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, UpdateView):
    model = TaskComments
    form_class = TaskCommentsForm
    template_name = 'apos/task_comment_update.html'
    success_url = reverse_lazy('task_comments')

    def form_valid(self, form):
        messages.success(self.request, 'Comment successfully updated!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['external_location'] = employee.external_location

        return kwargs


class TaskCommentsDeleteView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, DeleteView):
    model = TaskComments
    template_name = 'apos/task_comment_delete.html'
    success_url = reverse_lazy('task_comments')


class TaskAlertsListView(LoginRequiredMixin, OwnerOrManagementOrChefFullEmployeeLimitedPermissionMixin, ListView):
    model = TaskAlerts
    template_name = 'apos/task_alerts.html'


@login_required
def task_alerts_create(request):
    user = request.user
    employee = get_object_or_404(Employees, user=user)

    tasks_at_user = Tasks.objects.filter(employee_assignee=employee)

    for task in tasks_at_user:
        TaskAlerts.objects.create(task=task)
    
    return redirect('task_alerts')


class TaskAlertsDeleteView(LoginRequiredMixin, AllGroupsUserLocationFilteredMixin, DeleteView):
    model = TaskAlerts
    template_name = 'apos/task_alert_delete.html'
    success_url = reverse_lazy('task_alerts')


# Recipe management
class RecipesListView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, ListView):
    model = Recipes
    template_name = 'apos/recipes.html'


class RecipesCreateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, CreateView):
    model = Recipes
    form_class = RecipesForm
    template_name = 'apos/recipe_create.html'
    success_url = reverse_lazy('recipes')

    def form_valid(self, form):
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        form.instance.region_location = employee.region_location

        messages.success(self.request, f'Recipe \'{form.instance.recipe_name}\' successfully created!')
        return super().form_valid(form)


class RecipesUpdateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, UpdateView):
    model = Recipes
    form_class = RecipesForm
    template_name = 'apos/recipe_update.html'
    success_url = reverse_lazy('recipes')

    def form_valid(self, form):
        messages.success(self.request, 'Recipe successfully updated!')
        return super().form_valid(form)


class RecipesDeleteView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, DeleteView):
    model = Recipes
    template_name = 'apos/recipe_delete.html'
    success_url = reverse_lazy('recipes')


class RecipeIngredientsListView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, ListView):
    model = RecipeIngredients
    template_name = 'apos/recipe_ingredients.html'


class RecipeIngredientsCreateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, CreateView):
    model = RecipeIngredients
    form_class = RecipeIngredientsForm
    template_name = 'apos/recipe_ingredient_create.html'
    success_url = reverse_lazy('recipe_ingredients')

    def form_valid(self, form):
        messages.success(self.request, f'Ingredient \'{form.instance.ingredient_name}\' successfully added to {form.instance.recipe.recipe_name}!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)

        kwargs['region_location'] = employee.region_location
        kwargs['external_location'] = employee.external_location

        return kwargs


class RecipeIngredientsUpdateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, UpdateView):
    model = RecipeIngredients
    form_class = RecipeIngredientsForm
    template_name = 'apos/recipe_ingredient_update.html'
    success_url = reverse_lazy('recipe_ingredients')

    def form_valid(self, form):
        messages.success(self.request, 'Ingredient successfully updated!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)

        kwargs['region_location'] = employee.region_location
        kwargs['external_location'] = employee.external_location

        return kwargs


class RecipeIngredientsDeleteView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, DeleteView):
    model = RecipeIngredients
    template_name = 'apos/recipe_ingredient_delete.html'
    success_url = reverse_lazy('recipe_ingredients')


# Menu management
class MenuItemsListView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, ListView):
    model = MenuItems
    template_name = 'apos/menu_items.html'


class MenuItemsCreateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, CreateView):
    model = MenuItems
    form_class = MenuItemsForm
    template_name = 'apos/menu_item_create.html'
    success_url = reverse_lazy('menu_items')

    def form_valid(self, form):
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        form.instance.external_location = employee.external_location

        messages.success(self.request, f'Menu item \'{form.instance.item_name}\' successfully added to the menu!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['region_location'] = employee.region_location

        return kwargs


class MenuItemsUpdateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, UpdateView):
    model = MenuItems
    form_class = MenuItemsForm
    template_name = 'apos/menu_item_update.html'
    success_url = reverse_lazy('menu_items')

    def form_valid(self, form):
        messages.success(self.request, 'Menu item successfully updated!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['region_location'] = employee.region_location

        return kwargs


class MenuItemsDeleteView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, DeleteView):
    model = MenuItems
    template_name = 'apos/menu_item_delete.html'
    success_url = reverse_lazy('menu_items')


class AddOnsListView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, ListView):
    model = AddOns
    template_name = 'apos/add_ons.html'


class AddOnsCreateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, CreateView):
    model = AddOns
    form_class = AddOnsCreateForm
    template_name = 'apos/add_on_create.html'
    success_url = reverse_lazy('add_ons')

    def form_valid(self, form):
        messages.success(self.request, f'Add-on \'{form.instance.add_on_name}\' successfully created!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['external_location'] = employee.external_location

        return kwargs


class AddOnsUpdateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, UpdateView):
    model = AddOns
    form_class = AddOnsUpdateForm
    template_name = 'apos/add_on_update.html'
    success_url = reverse_lazy('add_ons')

    def form_valid(self, form):
        messages.success(self.request, 'Add-on successfully updated!')
        return super().form_valid(form)


class AddOnsDeleteView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, DeleteView):
    model = AddOns
    template_name = 'apos/add_on_delete.html'
    success_url = reverse_lazy('add_ons')


class MenuItemAddOnsListView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, ListView):
    model = MenuItemAddOns
    template_name = 'apos/menu_item_add_ons.html'


class MenuItemAddOnsCreateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, CreateView):
    model = MenuItemAddOns
    form_class = MenuItemAddOnsForm
    template_name = 'apos/menu_item_add_on_create.html'
    success_url = reverse_lazy('menu_item_add_ons')

    def form_valid(self, form):
        messages.success(self.request, f'\'{form.instance.add_on.add_on_name}\' successfully added to \'{form.instance.menu_item.item_name}\'!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['external_location'] = employee.external_location

        return kwargs


class MenuItemAddOnsDeleteView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, DeleteView):
    model = MenuItemAddOns
    template_name = 'apos/menu_item_add_on_delete.html'
    success_url = reverse_lazy('menu_item_add_ons')


class MenuItemOrdersListView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, ListView):
    model = MenuItemOrders
    template_name = 'apos/menu_item_orders.html'


@login_required
def menu_item_ordering_page(request):
    user = request.user
    employee = get_object_or_404(Employees, user=user)

    menu_items = MenuItems.objects.filter(external_location=employee.external_location)
    random_menu_item = menu_items.order_by('?').first().item_name if menu_items.exists() else 'Wait, there are no items on the menu... WHERE\'S THE CHEF? HELP! HELP!!!'

    tentative_suggestion = random.choice([
        'Maybe a... ', 
        'How about a... ', 
        'What about a... ', 
        'Did you ever try the... ', 
        'Try the... ', 
        'I would recommend the... '
    ])

    return render(request, 'apos/menu_item_ordering_page.html', {'menu_items': menu_items, 'random_menu_item': f'{tentative_suggestion}{random_menu_item}?'})


class MenuItemOrdersCreateView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, CreateView):
    model = MenuItemOrders
    form_class = MenuItemOrdersCreateForm
    template_name = 'apos/menu_item_order_create.html'
    success_url = reverse_lazy('menu_item_orders')

    def form_valid(self, form):
        menu_item_pk = self.kwargs.get('menu_item_pk')
        menu_item = get_object_or_404(MenuItems, pk=menu_item_pk)
        
        menu_item_order = form.save(commit=False)
        menu_item_order.menu_item = menu_item
        menu_item_order.save()
        form.save_m2m()

        messages.success(self.request, 'Order placed successfully!')
        return super().form_valid(form)


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        menu_item_pk = self.kwargs.get('menu_item_pk')
        kwargs['menu_item'] = menu_item_pk

        return kwargs


class MenuItemOrdersUpdateView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, UpdateView):
    model = MenuItemOrders
    form_class = MenuItemOrdersUpdateForm
    template_name = 'apos/menu_item_order_update.html'
    success_url = reverse_lazy('menu_item_orders')

    def form_valid(self, form):
        messages.success(self.request, f'Order status updated to {form.instance.order_status}!')
        return super().form_valid(form)


class MenuEngineeringReportsListView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, ListView):
    model = MenuEngineeringReports
    template_name = 'apos/menu_engineering_reports.html'


@login_required
def menu_engineering_report_create(request):
    user = request.user
    employee = get_object_or_404(Employees, user=user)

    if not user.groups.filter(name__in=['Owner', 'Management', 'Chef']).exists():
        messages.error(request, f'Woah there {employee.first_name}! Nothing to see here! Please go back :)')
        previous_url = request.META.get('HTTP_REFERER', 'home')
        return redirect(previous_url)
    
    menu_items_at_external_location = MenuItems.objects.filter(external_location=employee.external_location)

    for menu_item in menu_items_at_external_location:
        MenuEngineeringReports.objects.create(menu_item=menu_item)

    return redirect('menu_engineering_reports')


@login_required
def menu_engineering_report_delete_all(request):
    user = request.user
    employee = get_object_or_404(Employees, user=user)

    if not user.groups.filter(name__in=['Owner', 'Management', 'Chef']).exists():
        messages.error(request, f'Woah there {employee.first_name}! Nothing to see here! Please go back :)')
        previous_url = request.META.get('HTTP_REFERER', 'home')
        return redirect(previous_url)
    
    MenuEngineeringReports.objects.filter(
        external_location=employee.external_location
    ).delete()

    return redirect('menu_engineering_reports')


# Menu waste management
class WasteRecordsListView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, ListView):
    model = WasteRecords
    template_name = 'apos/waste_records.html'


class WasteRecordsCreateView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, CreateView):
    model = WasteRecords
    form_class = WasteRecordsForm
    template_name = 'apos/waste_record_create.html'
    success_url = reverse_lazy('waste_records')

    def form_valid(self, form):
        messages.success(self.request, f'Waste record for \'{form.instance.menu_item.item_name}\' recorded successfully!')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['external_location'] = employee.external_location

        return kwargs


class WasteRecordsUpdateView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, UpdateView):
    model = WasteRecords
    form_class = WasteRecordsForm
    template_name = 'apos/waste_record_update.html'
    success_url = reverse_lazy('waste_records')

    def form_valid(self, form):
        messages.success(self.request, 'Waste record updated successfully!')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['external_location'] = employee.external_location

        return kwargs


class WasteRecordsDeleteView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, DeleteView):
    model = WasteRecords
    template_name = 'apos/waste_record_delete.html'
    success_url = reverse_lazy('waste_records')


class WasteAnalysisListView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, ListView):
    model = WasteAnalysis
    template_name = 'apos/waste_analysis.html'


@login_required
def waste_analysis_create(request):
    user = request.user
    employee = get_object_or_404(Employees, user=user)

    if employee.job_position not in ['Owner', 'Manager', 'Chef', 'Cook', 'Kitchen assistant']:
        messages.error(request, f'Woah there {employee.first_name}! Nothing to see here! Please go back :)')
        return redirect('waste_analysis')

    menu_items_at_external_location = MenuItems.objects.filter(external_location=employee.external_location)

    for menu_items in menu_items_at_external_location:
        WasteAnalysis.objects.create(menu_item=menu_items)
    
    messages.success(request, 'Waste analysis records created successfully!')
    return redirect('waste_analysis')

@login_required
def waste_analysis_delete_all(request):
    user = request.user
    employee = get_object_or_404(Employees, user=user)

    if employee.job_position not in ['Owner', 'Manager', 'Chef', 'Cook', 'Kitchen assistant']:
        messages.error(request, f'Woah there {employee.first_name}! Nothing to see here! Please go back :)')
        return redirect('waste_analysis')

    WasteAnalysis.objects.filter(
        external_location=employee.external_location
    ).delete()

    messages.success(request, 'All waste analysis records deleted successfully!')
    return redirect('waste_analysis')


# Receipt creator + transactions log/tracker
class PaymentsListView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, ListView):
    model = Payments
    template_name = 'apos/payments.html'


class PaymentsCreateView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, CreateView):
    model = Payments
    form_class = PaymentsForm
    template_name = 'apos/payment_create.html'
    success_url = reverse_lazy('payment_success_receipt')

    def form_valid(self, form):
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        form.instance.employee = employee

        messages.success(self.request, f'Payment at table #{form.instance.internal_location} processed successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['external_location'] = employee.external_location

        return kwargs


@login_required
def payment_receipt_print(request):
    user = request.user
    employee = get_object_or_404(Employees, user=user)

    latest_payment = Payments.objects.filter(employee=employee).order_by('-payment_datetime').first()
    success_payment_msg = random.choice([
        'Payment successful ✓',
        'Woohoo!',
        'Payment successful!',
        'I\'ll take that!',
        'Nice tip :)',
        'Here\'s the receipt! >:('
    ])

    return render(request, 'apos/payment_receipt_print.html', {'latest_payment': latest_payment, 'success_payment_msg': success_payment_msg})


# Nutrition and allergen management
class NutritionAllergenInfoListView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, ListView):
    model = NutritionAllergenInfo
    template_name = 'apos/nutrition_allergen_info.html'


class NutritionAllergenInfoCreateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, CreateView):
    model = NutritionAllergenInfo
    form_class = NutritionAllergenInfoCreateForm
    template_name = 'apos/nutrition_allergen_info_create.html'
    success_url = reverse_lazy('nutrition_allergen_info')

    def form_valid(self, form):
        messages.success(self.request, f'Nutrition and allergen information for {form.instance.menu_item.item_name} created successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['external_location'] = employee.external_location

        return kwargs


class NutritionAllergenInfoUpdateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, UpdateView):
    model = NutritionAllergenInfo
    form_class = NutritionAllergenInfoUpdateForm
    template_name = 'apos/nutrition_allergen_info_update.html'
    success_url = reverse_lazy('nutrition_allergen_info')

    def form_valid(self, form):
        messages.success(self.request, f'Nutrition and allergen information updated successfully!')
        return super().form_valid(form)


class NutritionAllergenInfoDeleteView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, DeleteView):
    model = NutritionAllergenInfo
    template_name = 'apos/nutrition_allergen_info_delete.html'
    success_url = reverse_lazy('nutrition_allergen_info')


# Inventory cost reports
class AccountingPeriodsListView(LoginRequiredMixin, OwnerOrManagementRequiredMixin, ListView):
    model = AccountingPeriods
    template_name = 'apos/accounting_periods.html'


class AccountingPeriodsCreateView(LoginRequiredMixin, OwnerOrManagementRequiredMixin, CreateView):
    model = AccountingPeriods
    form_class = AccountingPeriodsForm
    template_name = 'apos/accounting_period_create.html'
    success_url = reverse_lazy('accounting_periods')

    def form_valid(self, form):
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        form.instance.region_location = employee.region_location

        messages.success(self.request, 'Accounting period added successfully!')
        return super().form_valid(form)


class AccountingPeriodsUpdateView(LoginRequiredMixin, OwnerOrManagementRequiredMixin, UpdateView):
    model = AccountingPeriods
    form_class = AccountingPeriodsForm
    template_name = 'apos/accounting_period_update.html'
    success_url = reverse_lazy('accounting_periods')

    def form_valid(self, form):
        messages.success(self.request, 'Accounting period updated successfully!')
        return super().form_valid(form)


class AccountingPeriodsDeleteView(LoginRequiredMixin, OwnerOrManagementRequiredMixin, DeleteView):
    model = AccountingPeriods
    template_name = 'apos/accounting_period_delete.html'
    success_url = reverse_lazy('accounting_periods')


class InventoryCostReportsListView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, ListView):
    model = InventoryCostReports
    template_name = 'apos/inventory_cost_reports.html'


@login_required
def inventory_cost_report_create(request):
    user = request.user
    employee = get_object_or_404(Employees, user=user)

    if not user.groups.filter(name__in=['Owner', 'Management', 'Chef']).exists():
        messages.error(request, f'Woah there {employee.first_name}! Nothing to see here! Please go back :)')
        previous_url = request.META.get('HTTP_REFERER', 'home')
        return redirect(previous_url)

    InventoryCostReports.objects.create(external_location=employee.external_location)

    messages.success(request, 'Inventory cost report created successfully!')
    return redirect('inventory_cost_reports')


class InventoryUsageListView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, ListView):
    model = InventoryUsage
    template_name = 'apos/inventory_usage.html'


@login_required
def inventory_usage_create(request):
    user = request.user
    employee = get_object_or_404(Employees, user=user)

    if not user.groups.filter(name__in=['Owner', 'Management', 'Chef']).exists():
        messages.error(request, f'Woah there {employee.first_name}! Nothing to see here! Please go back :)')
        previous_url = request.META.get('HTTP_REFERER', 'home')
        return redirect(previous_url)

    inventory_item_at_external_location = InventoryItems.objects.filter(external_location=employee.external_location)

    for inventory_item in inventory_item_at_external_location:
        InventoryUsage.objects.create(inventory_item=inventory_item)
    
    messages.success(request, 'Inventory usage report created successfully!')
    return redirect('inventory_usage')


class InventoryTransfersListView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, ListView):
    model = InventoryTransfers
    template_name = 'apos/inventory_transfers.html'


class InventoryTransfersCreateView(LoginRequiredMixin, OwnerOrManagementOrChefRequiredMixin, CreateView):
    model = InventoryTransfers
    form_class = InventoryTransfersForm
    template_name = 'apos/inventory_transfer_create.html'
    success_url = reverse_lazy('inventory_transfers')

    def form_valid(self, form):
        messages.success(self.request, 'Inventory transfer recorded successfully!')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)

        kwargs['region_location'] = employee.region_location
        kwargs['external_location'] = employee.external_location

        return kwargs


class InventoryTransfersUpdateView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, UpdateView):
    model = InventoryTransfers
    form_class = InventoryTransfersForm
    template_name = 'apos/inventory_transfer_update.html'
    success_url = reverse_lazy('inventory_transfers')

    def form_valid(self, form):
        messages.success(self.request, 'Inventory transfer updated successfully!')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)

        kwargs['region_location'] = employee.region_location
        kwargs['external_location'] = employee.external_location

        return kwargs


class InventoryTransfersDeleteView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, DeleteView):
    model = InventoryTransfers
    template_name = 'apos/inventory_transfer_delete.html'
    success_url = reverse_lazy('inventory_transfers')


class InventoryTransfersInternalListView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, ListView):
    model = InventoryTransfers
    template_name = 'apos/inventory_transfers_internal.html'


class InventoryTransfersInternalCreateView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, CreateView):
    model = InventoryTransfersInternal
    form_class = InventoryTransfersInternalForm
    template_name = 'apos/inventory_transfer_internal_create.html'
    success_url = reverse_lazy('inventory_transfers_internal')

    def form_valid(self, form):
        messages.success(self.request, 'Inventory transfer (internal/inside the building) recorded successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        inventory_transfer_pk = self.kwargs.get('inventory_transfer_pk')
        kwargs['inventory_transfer'] = inventory_transfer_pk

        return kwargs


class InventoryTransfersInternalUpdateView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, UpdateView):
    model = InventoryTransfersInternal
    form_class = InventoryTransfersInternalForm
    template_name = 'apos/inventory_transfer_internal_update.html'
    success_url = reverse_lazy('inventory_transfers_internal')

    def form_valid(self, form):
        messages.success(self.request, 'Inventory transfer (internal/inside the building) updated successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        inventory_transfer_pk = self.kwargs.get('pk')
        kwargs['inventory_transfer'] = inventory_transfer_pk

        return kwargs


class InventoryTransfersInternalDeleteView(LoginRequiredMixin, AllGroupsLocationFilteredMixin, DeleteView):
    model = InventoryTransfersInternal
    template_name = 'apos/inventory_transfer_internal_delete.html'
    success_url = reverse_lazy('inventory_transfers_internal')


class InventoryWasteBinListView(LoginRequiredMixin, AllGroupsUserLocationFilteredMixin, ListView):
    model = InventoryWasteBin
    template_name = 'apos/inventory_waste_bin.html'


class InventoryWasteBinCreateView(LoginRequiredMixin, AllGroupsUserLocationFilteredMixin, CreateView):
    model = InventoryWasteBin
    form_class = InventoryWasteBinForm
    template_name = 'apos/inventory_waste_bin_create.html'
    success_url = reverse_lazy('inventory_waste_bin')

    def form_valid(self, form):
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        form.instance.employee_reporter = employee
        
        messages.success(self.request, f'Wastage caused by {form.instance.employee_culprit} recorded successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['external_location'] = employee.external_location

        return kwargs


class InventoryWasteBinUpdateView(LoginRequiredMixin, AllGroupsUserLocationFilteredMixin, UpdateView):
    model = InventoryWasteBin
    form_class = InventoryWasteBinForm
    template_name = 'apos/inventory_waste_bin_update.html'
    success_url = reverse_lazy('inventory_waste_bin')

    def form_valid(self, form):
        messages.success(self.request, 'Wastage updated successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['external_location'] = employee.external_location
        
        return kwargs


class InventoryWasteBinDeleteView(LoginRequiredMixin, AllGroupsUserLocationFilteredMixin, DeleteView):
    model = InventoryWasteBin
    template_name = 'apos/inventory_waste_bin_delete.html'
    success_url = reverse_lazy('inventory_waste_bin')


# Tip management
class EmployeeTipRecordsListView(LoginRequiredMixin, AllGroupsUserLocationFilteredMixin, ListView):
    model = EmployeeTipRecords
    template_name = 'apos/employee_tip_records.html'


class EmployeeTipRecordsCreateView(LoginRequiredMixin, AllGroupsUserLocationFilteredMixin, CreateView):
    model = EmployeeTipRecords
    form_class = EmployeeTipRecordsForm
    template_name = 'apos/employee_tip_record_create.html'
    success_url = reverse_lazy('employee_tip_records')

    def form_valid(self, form):
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)

        form.instance.external_location = employee.external_location
        form.instance.employee = employee
        form.instance.daily_shift_record = DailyShiftRecords.objects.filter(
            external_location=employee.external_location,
            employee=employee,
            shift_date=date.today(),
            punch_in_time__isnull=False,
            punch_out_time__isnull=True
        ).first()

        messages.success(self.request, f'Tip amount of {form.instance.tip_amount} recorded successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['external_location'] = employee.external_location

        return kwargs


class EmployeeTipRecordsUpdateView(LoginRequiredMixin, AllGroupsUserLocationFilteredMixin, UpdateView):
    model = EmployeeTipRecords
    form_class = EmployeeTipRecordsForm
    template_name = 'apos/employee_tip_record_update.html'
    success_url = reverse_lazy('employee_tip_records')

    def form_valid(self, form):
        messages.success(self.request, 'Tip record updated successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        kwargs['external_location'] = employee.external_location

        return kwargs
    

class TipPoolingRecordsListView(LoginRequiredMixin, OwnerOrManagementRequiredMixin, ListView):
    model = TipPoolingRecords
    template_name = 'apos/tip_pooling_records.html'


class TipPoolingRecordsCreateView(LoginRequiredMixin, OwnerOrManagementRequiredMixin, CreateView):
    model = TipPoolingRecords
    form_class = TipPoolingRecordsForm
    template_name = 'apos/tip_pooling_record_create.html'
    success_url = reverse_lazy('tip-pooling_records')

    def form_valid(self, form):
        user = self.request.user
        employee = get_object_or_404(Employees, user=user)
        form.instance.external_location = employee.external_location

        if form.instance.calculate_or_send_tips == 'calculate':
            messages.success(self.request, f'Tip pooling record calculated and recorded successfully!')
        else:
            messages.success(self.request, f'Tip pooling record calculated, recorded, and sent to your employees successfully!')

        return super().form_valid(form)


class EmployeeTipPayoutsListView(LoginRequiredMixin, OwnerOrManagementFullChefOrEmployeeLimitedPermissionMixin, ListView):
    model = EmployeeTipPayouts
    template_name = 'apos/employee_tip_payouts.html'
