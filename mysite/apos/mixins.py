from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.db import OperationalError
from django.db.models import Q
from .models import Employees


# Full permissions mixins; only this group can CRUD this model
class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Owner').exists()
    
    def handle_no_permission(self):
        try:
            employee = Employees.objects.get(account_username=self.request.user.username)
            messages.error(self.request, f'Woah there {employee.first_name}! Nothing to see here! Go back :)')
    
            previous_url = self.request.META.get('HTTP_REFERER', 'home')
            return redirect(previous_url)
            
        except OperationalError:
            messages.error(self.request, 'Create an account, log back in, or add yourself to \'Employees\' to get started')
            return redirect('home')

    def is_management_or_chef_or_employee(self):
        return not self.test_func()

    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            employee = Employees.objects.get(
                account_username=self.request.user.username
            )

            return queryset.filter(
                Q(unique_identifier=employee.unique_identifier) |
                Q(region_location=employee.region_location) |
                Q(external_location=employee.external_location) |
                Q(source_external_location=employee.external_location) |
                Q(destination_external_location=employee.external_location)
            )

        except OperationalError:
            messages.error(self.request, 'Create an account, log back in, or add yourself to \'Employees\' to get started')
            return redirect('home')


class OwnerOrManagementRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Owner', 'Management']).exists()
    
    def handle_no_permission(self):
        try:
            employee = Employees.objects.get(account_username=self.request.user.username)
            messages.error(self.request, f'Woah there {employee.first_name}! Nothing to see here! Go back :)')

            previous_url = self.request.META.get('HTTP_REFERER', 'home')
            return redirect(previous_url)
        
        except OperationalError:
            messages.error(self.request, 'Create an account, log back in, or add yourself to \'Employees\' to get started')
            return redirect('home')

    def is_chef_or_employee(self):
        return not self.test_func()

    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            employee = Employees.objects.get(
                account_username=self.request.user.username
            )

            return queryset.filter(
                Q(unique_identifier=employee.unique_identifier) |
                Q(region_location=employee.region_location) |
                Q(external_location=employee.external_location) |
                Q(source_external_location=employee.external_location) |
                Q(destination_external_location=employee.external_location)
            )

        except OperationalError:
            messages.error(self.request, 'Create an account, log back in, or add yourself to \'Employees\' to get started')
            return redirect('home')


class OwnerOrManagementOrChefRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Owner', 'Management', 'Chef']).exists()

    def handle_no_permission(self):
        try:
            employee = Employees.objects.get(account_username=self.request.user.username)
            messages.error(self.request, f'Woah there {employee.first_name}! Nothing to see here! Go back :)')

            previous_url = self.request.META.get('HTTP_REFERER', 'home')
            return redirect(previous_url)
            
        except OperationalError:
            messages.error(self.request, 'Create an account, log back in, or add yourself to \'Employees\' to get started')
            return redirect('home')

    def is_employee(self):
        return not self.test_func()

    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            employee = Employees.objects.get(
                account_username=self.request.user.username
            )

            return queryset.filter(
                Q(unique_identifier=employee.unique_identifier) |
                Q(region_location=employee.region_location) |
                Q(external_location=employee.external_location) |
                Q(source_external_location=employee.external_location) |
                Q(destination_external_location=employee.external_location)
            )
            
        except OperationalError:
            messages.error(self.request, 'Create an account, log back in, or add yourself to \'Employees\' to get started')
            return redirect('home')


class AllGroupsLocationFilteredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Owner', 'Management', 'Chef', 'Employee']).exists()

    def handle_no_permission(self):
        try:
            employee = Employees.objects.get(account_username=self.request.user.username)
            messages.error(self.request, f'Woah there {employee.first_name}! Nothing to see here! Go back :)')

            previous_url = self.request.META.get('HTTP_REFERER', 'home')
            return redirect(previous_url)

        except OperationalError:
            messages.error(self.request, 'Create an account, log back in, or add yourself to \'Employees\' to get started')
            return redirect('home')

    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            employee = Employees.objects.get(
                account_username=self.request.user.username
            )

            return queryset.filter(
                Q(unique_identifier=employee.unique_identifier) |
                Q(region_location=employee.region_location) |
                Q(external_location=employee.external_location) |
                Q(source_external_location=employee.external_location) |
                Q(destination_external_location=employee.external_location)
            )

        except OperationalError:
            messages.error(self.request, 'Create an account, log back in, or add yourself to \'Employees\' to get started')
            return redirect('home')


class AllGroupsUserLocationFilteredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Owner', 'Management', 'Chef', 'Employee']).exists()

    def handle_no_permission(self):
        try:
            employee = Employees.objects.get(account_username=self.request.user.username)
            messages.error(self.request, f'Woah there {employee.first_name}! Nothing to see here! Go back :)')

            previous_url = self.request.META.get('HTTP_REFERER', 'home')
            return redirect(previous_url)

        except OperationalError:
            messages.error(self.request, 'Create an account, log back in, or add yourself to \'Employees\' to get started')
            return redirect('home')

    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            employee = Employees.objects.get(
                account_username=self.request.user.username
            )

            return queryset.filter(
                Q(unique_identifier=employee.unique_identifier) |
                Q(employee=employee) |
                Q(employee_requestor=employee) |
                Q(employee_responder=employee) |
                Q(employee_swapped=employee) |
                Q(employee_assignee=employee) |
                Q(employee_assignor=employee) |
                Q(employee_tasker=employee) |
                Q(employee_commenter=employee) |
                Q(employee_culprit=employee) |
                Q(employee_reporter=employee) |
                Q(region_location=employee.region_location) |
                Q(external_location=employee.external_location) |
                Q(source_external_location=employee.external_location) |
                Q(destination_external_location=employee.external_location)
            )
        
        except OperationalError:
            messages.error(self.request, 'Create an account, log back in, or add yourself to \'Employees\' to get started')
            return redirect('home')


# Full and limited permissions mixins; specific groups can CRUD; others can only do the 'R'
class OwnerFullManagementOrChefOrEmployeeLimitedPermissionMixin(OwnerRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if self.is_management_or_chef_or_employee():
            if self.request.method != 'GET':
                try:
                    employee = Employees.objects.get(account_username=self.request.user.username)
                    messages.error(self.request, f'Woah there {employee.first_name}! Nothing to see here! Go back :)')

                    previous_url = self.request.META.get('HTTP_REFERER', 'home')
                    return redirect(previous_url)
                
                except OperationalError:
                    messages.error(self.request, 'Create an account, log back in, or add yourself to \'Employees\' to get started')
                    return redirect('home')

            else:
                return super().dispatch(request, *args, **kwargs)

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        try:
            queryset = super().get_queryset()

            if self.is_management_or_chef_or_employee():
                employee = Employees.objects.get(
                    account_username=self.request.user.username
                )

                return queryset.filter(
                    Q(employee=employee) |
                    Q(employee_requestor=employee) |
                    Q(employee_responder=employee) |
                    Q(employee_swapped=employee) |
                    Q(employee_assignee=employee) |
                    Q(employee_assignor=employee) |
                    Q(employee_tasker=employee) |
                    Q(employee_commenter=employee) |
                    Q(employee_culprit=employee) |
                    Q(employee_reporter=employee) |
                    Q(region_location=employee.region_location) |
                    Q(external_location=employee.external_location) |
                    Q(source_external_location=employee.external_location) |
                    Q(destination_external_location=employee.external_location)
                )

            return queryset

        except OperationalError:
            messages.error(self.request, 'Create an account, log back in, or add yourself to \'Employees\' to get started')
            return redirect('home')


class OwnerOrManagementFullChefOrEmployeeLimitedPermissionMixin(OwnerOrManagementRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if self.is_chef_or_employee():
            if self.request.method != 'GET':
                try:
                    employee = Employees.objects.get(account_username=self.request.user.username)
                    messages.error(self.request, f'Woah there {employee.first_name}! Nothing to see here! Go back :)')
    
                    previous_url = self.request.META.get('HTTP_REFERER', 'home')
                    return redirect(previous_url)

                except OperationalError:
                    messages.error(self.request, 'Create an account, log back in, or add yourself to \'Employees\' to get started')
                    return redirect('home')

            else:
                return super().dispatch(request, *args, **kwargs)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        try:
            queryset = super().get_queryset()

            if self.is_chef_or_employee():
                employee = Employees.objects.get(
                    account_username=self.request.user.username
                )

                return queryset.filter(
                    Q(employee=employee) |
                    Q(employee_requestor=employee) |
                    Q(employee_responder=employee) |
                    Q(employee_swapped=employee) |
                    Q(employee_assignee=employee) |
                    Q(employee_assignor=employee) |
                    Q(employee_tasker=employee) |
                    Q(employee_commenter=employee) |
                    Q(employee_culprit=employee) |
                    Q(employee_reporter=employee) |
                    Q(region_location=employee.region_location) |
                    Q(external_location=employee.external_location) |
                    Q(source_external_location=employee.external_location) |
                    Q(destination_external_location=employee.external_location)
                )

            return queryset
        
        except OperationalError:
            messages.error(self.request, 'Create an account, log back in, or add yourself to \'Employees\' to get started')
            return redirect('home')


class OwnerOrManagementOrChefFullEmployeeLimitedPermissionMixin(OwnerOrManagementOrChefRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if self.is_employee():
            if self.request.method != 'GET':
                try:
                    employee = Employees.objects.get(account_username=self.request.user.username)
                    messages.error(self.request, f'Woah there {employee.first_name}! Nothing to see here! Go back :)')

                    previous_url = self.request.META.get('HTTP_REFERER', 'home')
                    return redirect(previous_url)
                
                except OperationalError:
                    messages.error(self.request, 'Create an account, log back in, or add yourself to \'Employees\' to get started')
                    return redirect('home')

            else:
                return super().dispatch(request, *args, **kwargs)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        try:
            queryset = super().get_queryset()

            if self.is_employee():
                employee = Employees.objects.get(
                    account_username=self.request.user.username
                )

                return queryset.filter(
                    Q(employee=employee) |
                    Q(employee_requestor=employee) |
                    Q(employee_responder=employee) |
                    Q(employee_swapped=employee) |
                    Q(employee_assignee=employee) |
                    Q(employee_assignor=employee) |
                    Q(employee_tasker=employee) |
                    Q(employee_commenter=employee) |
                    Q(employee_culprit=employee) |
                    Q(employee_reporter=employee) |
                    Q(region_location=employee.region_location) |
                    Q(external_location=employee.external_location) |
                    Q(source_external_location=employee.external_location) |
                    Q(destination_external_location=employee.external_location)
                )

            return queryset
        
        except OperationalError:
            messages.error(self.request, 'Create an account, log back in, or add yourself to \'Employees\' to get started')
            return redirect('home')
