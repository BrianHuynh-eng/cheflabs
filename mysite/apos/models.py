from datetime import datetime, time
from phonenumber_field.modelfields import PhoneNumberField

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password


# TODO: LocationTrainingInsights: Add logic for KeplerPro suggestions


class CustomUser(AbstractUser):
   phone_number = PhoneNumberField(null=False, blank=False, unique=True)


# Location management
class RegionLocations(models.Model):
   unique_identifier = models.CharField(max_length=12, blank=True)

   state_or_province_name = models.TextField()
   country_name = models.TextField()
   overtime_threshold = models.PositiveIntegerField()


class ExternalLocations(models.Model):
   region_location = models.ForeignKey(RegionLocations, null=True, blank=True, on_delete=models.CASCADE)
   location_name = models.CharField(max_length=200)
   address = models.TextField()
   contact_person = models.CharField(max_length=100)


class InternalLocations(models.Model): 
   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)
   location_name = models.TextField() # Anything that is internal (table #, freezer, pantry, etc.)


class LocationTrainingInsights(models.Model):
   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)
   variance_faults = models.PositiveIntegerField()
   suggested_training = models.TextField()
   last_updated = models.DateField(auto_now=True)
   
   @property
   def variance_faults_status(self):
      return "High" if self.variance_faults > 3 else "Low"


# Employee management
class Employees(models.Model):
   JOB_POSITION_CHOICES = [
      ('Owner', 'Owner'),
      ('Manager', 'Manager'), 
      ('Chef', 'Chef'), 
      ('Cook', 'Cook'), 
      ('Kitchen assistant', 'Kitchen assistant'),
      ('Waiter', 'Waiter'), 
      ('Bartender', 'Bartender'), 
      ('Cashier', 'Cashier'), 
      ('Cleaner', 'Cleaner')
   ]

   region_location = models.ForeignKey(RegionLocations, null=True, blank=True, on_delete=models.CASCADE)
   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.SET_NULL)
   
   user = models.OneToOneField(CustomUser, null=True, blank=True, on_delete=models.CASCADE)
   unique_identifier = models.CharField(max_length=12, blank=True) # For owner use only; cannot be changed once created
   first_name = models.CharField(max_length=100)
   last_name = models.CharField(max_length=100)
   email = models.EmailField(max_length=100)
   phone = PhoneNumberField(null=False, blank=False, unique=True)
   hire_date = models.DateField()
   job_position = models.CharField(max_length=18, choices=JOB_POSITION_CHOICES)
   account_username = models.CharField(max_length=128, blank=True)
   account_password = models.CharField(max_length=128)
   hourly_wage = models.DecimalField(max_digits=10, decimal_places=2)
   is_training_complete = models.BooleanField(default=False) 
   availability = models.JSONField()
   notes = models.CharField(max_length=150, blank=True)

   @property
   def get_account_username(self):
      if len(first_name) >= 3 and len(last_name) >= 3:
         return (first_name[:3] + last_name[:3] + phone[-2] + job_position[0].upper()).replace(' ', '')
      else:
         return (first_name[:2] + last_name[:2] + phone[-2] + job_position[0].upper()).replace(' ', '')

   @property
   def get_account_password(self):
      if len(first_name) >= 3 and len(last_name) >= 3:
         return (first_name[:3] + last_name[:3] + phone[-2] + job_position[0].upper() + '@' + email[:3]).replace(' ', '')
      else:
         return (first_name[:2] + last_name[:2] + phone[-2] + job_position[0].upper() + '@' + email[:3]).replace(' ', '')

   def save(self, *args, **kwargs):
      self.account_username = self.get_account_username
      self.account_password = make_password(self.get_account_password)
      
      super().save(*args, **kwargs)


class EmployeesPerformance(models.Model):
   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True,  on_delete=models.CASCADE)

   employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
   total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
   total_tips_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
   total_hours_worked = models.DecimalField(max_digits=10, decimal_places=1, default=0)
   total_overtime_hours_worked = models.DecimalField(max_digits=10, decimal_places=1, default=0)
   late_to_work_count = models.PositiveIntegerField(default=0)
   missed_work_days_count = models.PositiveIntegerField(default=0)
   uncompleted_shift_count = models.PositiveIntegerField(default=0)
   requests_created = models.PositiveIntegerField(default=0)
   total_transactions_completed = models.PositiveIntegerField(default=0)
   total_sales_handled_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
   total_breaks_taken = models.PositiveIntegerField(default=0)
   total_break_time = models.DecimalField(max_digits=10, decimal_places=1, default=0)
   total_inventory_waste_count = models.PositiveIntegerField(default=0)

   @property
   def get_external_location(self):
      return self.employee.external_location

   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      super().save(*args, **kwargs)

   
class Requests(models.Model):
   REQUEST_TYPE_CHOICES = [
      ('Shift change', 'Shift change'), 
      ('Shift swap', 'Shift swap'), 
      ('Time-off/Absence', 'Time-off/Absence'), 
      ('Overtime', 'Overtime'), ('Raise', 'Raise'), 
      ('Report employee', 'Report employee'), 
      ('Report complaint', 'Report complaint'), 
      ('Other', 'Other')
   ]

   REQUEST_STATUS_CHOICES = [
      ('Pending', 'Pending'), 
      ('Approved/Resolved', 'Approved/Resolved'), 
      ('Denied', 'Denied')
   ]

   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   request_type = models.CharField(max_length=16, choices=REQUEST_TYPE_CHOICES)
   request_message = models.TextField()
   employee_requestor = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='employee_requestor')
   request_date = models.DateTimeField(auto_now_add=True)
   request_status = models.CharField(max_length=17, choices=REQUEST_STATUS_CHOICES, default='Pending')
   request_response = models.TextField()
   employee_responder = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='employee_responder')
   response_date = models.DateTimeField(auto_now=True)

   @property
   def get_external_location(self):
      return self.employee.external_location

   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      super().save(*args, **kwargs)

      employee_performance = EmployeesPerformance.objects.get_or_create(employee=self.employee_requestor)
      employee_performance.requests_created += 1
      employee_performance.save()


# Shift scheduling management
class ShiftScheduling(models.Model):
   SHIFT_TYPE_CHOICES = [
      ('Breakfast', 'Breakfast'), 
      ('Lunch', 'Lunch'), 
      ('Dinner', 'Dinner'), 
      ('Half', 'Half'), 
      ('Full', 'Full')
   ]

   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   employee = models.ForeignKey(Employees, on_delete=models.CASCADE, null=True, blank=True, related_name='orignal_employee')
   job_position = models.TextField()
   shift_type = models.CharField(max_length=9, choices=SHIFT_TYPE_CHOICES)
   start_time = models.TimeField()
   end_time = models.TimeField()
   total_hours = models.DecimalField(max_digits=10, decimal_places=1)
   shift_date = models.DateField()
   employee_swapped = models.ForeignKey(Employees, on_delete=models.CASCADE, null=True, blank=True, related_name='employee_swapped')
   is_open_shift = models.BooleanField(default=False)

   @property
   def get_external_location(self):
      return employee.external_location

   @property
   def get_job_position(self):
      return self.employee.job_position

   @property
   def calc_total_hours(self):
      start = datetime.combine(self.shift_date, self.start_time)
      end = datetime.combine(self.shift_date, self.end_time)
      return (end - start).total_seconds() / 3600

   def save(self, *args, **kwargs):
      self.external_location = get_external_location
      self.job_position = self.get_job_position
      self.total_hours = self.calc_total_hours

      super().save(*args, **kwargs)

      if self.employee:
         DailyShiftRecords.objects.create(
            external_location=self.external_location,
            employee=self.employee,
            shift_scheduling=self.pk,
            shift_type=self.shift_type,
            shift_date=self.shift_date,
            status='Upcoming'
         )
      
      if self.employee_swapped:
         DailyShiftRecords.objects.create(
            external_location=self.external_location,
            employee=self.employee_swapped,
            shift_scheduling=self.pk,
            shift_type=self.shift_type,
            shift_date=self.shift_date,
            status='Upcoming'
         )

         original_employee_daily_shift_record = DailyShiftRecords.objects.filter(
            external_location=self.external_location,
            employee=self.employee,
            shift_scheduling=self.pk,
            shift_type=self.shift_type,
            shift_date=self.shift_date,
            status='Upcoming'
         ).first()

         original_employee_daily_shift_record.status = 'SWAPPED'
         original_employee_daily_shift_record.save()


class DailyShiftRecords(models.Model):
   SHIFT_TYPE_CHOICES = [
      ('Breakfast', 'Breakfast'), 
      ('Lunch', 'Lunch'), 
      ('Dinner', 'Dinner'), 
      ('Half', 'Half'), 
      ('Full', 'Full')
   ]

   STATUS_CHOICES = [
      ('Upcoming', 'Upcoming'), 
      ('Late', 'Late'), 
      ('In-progress', 'In-progress'), 
      ('Completed', 'Completed'), 
      ('Uncompleted', 'Uncompleted'), 
      ('Missed', 'Missed'),
      ('SWAPPED', 'SWAPPED')
   ]

   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
   shift_scheduling = models.ForeignKey(ShiftScheduling, on_delete=models.CASCADE)
   shift_type = models.CharField(max_length=9, choices=SHIFT_TYPE_CHOICES)
   shift_date = models.DateField()
   punch_in_time = models.TimeField(null=True, blank=True) # Null/blank will be updated once the employee clocks in
   punch_out_time = models.TimeField(null=True, blank=True) # Null/blank will be updated once the employee clocks out
   total_hours_worked = models.DecimalField(max_digits=10, decimal_places=1)
   earnings = models.DecimalField(max_digits=10, decimal_places=2)
   status = models.CharField(max_length=11, choices=STATUS_CHOICES, default='Upcoming')

   @property
   def calc_total_hours_worked(self):
      if self.punch_in_time and self.punch_out_time:
         punch_in = datetime.combine(datetime.min, self.punch_in_time)
         punch_out = datetime.combine(datetime.min, self.punch_out_time)
         return (punch_out - punch_in).total_seconds() / 3600
      
      return 0

   @property
   def calc_earnings(self):
      return self.employee.hourly_wage * self.calc_total_hours_worked

   def save(self, *args, **kwargs):
      self.total_hours_worked = self.calc_total_hours_worked
      self.earnings = self.calc_earnings

      if self.punch_in_time:
         if self.punch_in_time - self.shift_scheduling.start_time > timedelta(minutes=7):
            self.status = 'Late'

            employee_performance = EmployeesPerformance.objects.get_or_create(employee=self.employee)
            employee_performance.late_to_work_count += 1
            employee_performance.save()

         else:
            self.status = 'In-progress'

         if self.punch_out_time:
            if self.punch_out_time >= self.shift_scheduling.end_time:
               self.status = 'Completed'

            if self.punch_out_time < self.shift_scheduling.end_time:
               self.status = 'Uncompleted'

               employee_performance = EmployeesPerformance.objects.get_or_create(employee=self.employee)
               employee_performance.uncompleted_shift_count += 1
               employee_performance.save()
      
      if self.status == 'Missed':
         employee_performance = EmployeesPerformance.objects.get_or_create(employee=self.employee)
         employee_performance.missed_work_days_count += 1
         employee_performance.save()

      super().save(*args, **kwargs)

      if self.punch_in_time and self.punch_out_time:
         week_shift_record = WeeklyShiftRecords.objects.filter(
            employee=self.employee,
            start_week_date__lte=self.shift_date,
            end_week_date__gte=self.shift_date
         ).first()
         
         if not week_shift_record:
            WeeklyShiftRecords.objects.create(
               external_location=self.external_location,
               employee=self.employee,
               start_week_date=self.shift_date - timedelta(days=self.shift_date.weekday()),
               end_week_date=self.shift_date + timedelta(days=(6 - self.shift_date.weekday())),
               regular_hours_worked=self.total_hours_worked,
               overtime_hours_worked=0,
               earnings_this_week=self.earnings
            )

         else:
            regular_hours_worked_added = week_shift_record.regular_hours_worked + self.total_hours_worked

            if regular_hours_worked_added > self.external_location.region_location.overtime_threshold:
               earnings_with_overtime = (
                  ((self.employee.hourly_wage 
                  * (regular_hours_worked_added - 40)) 
                  * 1.5) 
                  + (self.employee.hourly_wage 
                  * (self.total_hours_worked 
                  - (self.regular_hours_worked_added - 40)))
               )

               week_shift_record.overtime_hours_worked += regular_hours_worked_added - 40
               week_shift_record.regular_hours_worked = 40
               week_shift_record.earnings_this_week += earnings_with_overtime

               employee_performance = EmployeesPerformance.objects.get_or_create(employee=self.employee)
               employee_performance.total_earnings += earnings_with_overtime
               employee_performance.total_hours_worked += self.total_hours_worked
               employee_performance.total_overtime_hours_worked += regular_hours_worked_added - 40
               employee_performance.save()

            else:
               week_shift_record.regular_hours_worked += self.total_hours_worked
               week_shift_record.earnings_this_week += self.earnings

               employee_performance = EmployeesPerformance.objects.get_or_create(employee=self.employee)
               employee_performance.total_earnings += self.earnings
               employee_performance.total_hours_worked += self.total_hours_worked
               employee_performance.save()
            
            week_shift_record.save()


class WeeklyShiftRecords(models.Model):
   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
   start_week_date = models.DateField()
   end_week_date = models.DateField()
   regular_hours_worked = models.DecimalField(max_digits=10, decimal_places=1)
   overtime_hours_worked = models.DecimalField(max_digits=10, decimal_places=1)
   earnings_this_week = models.DecimalField(max_digits=10, decimal_places=2)


class BreakRecords(models.Model):
   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
   daily_shift_record = models.ForeignKey(DailyShiftRecords, on_delete=models.CASCADE)
   start_break_time = models.TimeField()
   end_break_time = models.TimeField()
   break_duration = models.PositiveIntegerField()
   break_date = models.DateField(auto_now_add=True)

   @property
   def get_external_location(self):
      return self.employee.external_location

   @property
   def get_daily_shift_record(self):
      return DailyShiftRecords.objects.filter(
         external_location=self.external_location,
         employee=self.employee,
         shift_date=self.break_date
      ).first()

   @property
   def calc_break_duration(self):
      start = datetime.combine(self.break_date, self.start_break_time)
      end = datetime.combine(self.break_date, self.end_break_time)
      return int(round((end - start).total_seconds() / 3600, 0))
   
   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      self.daily_shift_record = self.get_daily_shift_record
      self.break_duration = self.calc_break_duration

      super().save(*args, **kwargs)

      employee_performance = EmployeesPerformance.objects.get_or_create(employee=self.employee)
      employee_performance.total_breaks_taken += 1
      employee_performance.total_break_time += self.break_duration
      employee_performance.save()


# Inventory management
class InventoryItems(models.Model):
   ITEM_TYPE_CHOICES = [
      ('Ingredient', 'Ingredient'), 
      ('Nonfood', 'Nonfood')
   ]

   UNIT_OF_MEASUREMENT_CHOICES = [
      ('kg', 'kg'), 
      ('lbs', 'lbs'), 
      ('ml', 'ml'), 
      ('mm', 'mm'),
      ('L', 'L'), 
      ('pcs', 'pcs'), 
      ('oz', 'oz'), 
      ('g', 'g'),
      ('fl oz', 'fl oz'),
      ('cups', 'cups'), 
      ('qt', 'qt'),
      ('gal', 'gal'), 
      ('in', 'in'), 
      ('cm', 'cm')
   ]

   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   item_name = models.CharField(max_length=100)
   item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
   quantity = models.DecimalField(max_digits=10, decimal_places=3) # Enter existing inventory (0 if none; quantity added via OrderInventory)
   par_level = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, default=None)
   total_value = models.DecimalField(max_digits=10, decimal_places=2)
   unit_of_measurement = models.CharField(max_length=5, choices=UNIT_OF_MEASUREMENT_CHOICES)
   barcode = models.TextField()
   safety_stock = models.DecimalField(max_digits=10, decimal_places=2)
   deliveries_per_week = models.PositiveIntegerField()
   last_updated = models.DateTimeField(auto_now=True)

   @property
   def avg_unit_price(self):
      return self.total_value / self.quantity


class InventoryChecks(models.Model):
   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   inventory_item = models.ForeignKey(InventoryItems, on_delete=models.CASCADE)
   expected_quantity = models.DecimalField(max_digits=10, decimal_places=3)
   actual_quantity = models.DecimalField(max_digits=10, decimal_places=3)
   employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
   check_date = models.DateField(auto_now_add=True)

   @property
   def get_external_location(self):
      return self.inventory_item.external_location

   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      super().save(*args, **kwargs)

      variance_percentage = (
         (self.actual_quantity - self.expected_quantity)
         / self.expected_quantity
         * 100
      )

      if variance_percentage >= 5:
         location_training_insights = LocationTrainingInsights.objects.get(
            external_location=self.external_location
         )

         if not location_training_insights:
            LocationTrainingInsights.objects.create(
               external_location=self.external_location,
               variance_faults=1,
               suggested_training='TBC', # Use KeplerPro to generate suggestions
            )
         else:
            location_training_insights.variance_faults += 1
            location_training_insights.suggested_training = 'TBC' # Use KeplerPro to generate suggestions
            location_training_insights.save()


# Vendor management
class Vendors(models.Model):
   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   name = models.TextField()
   email = models.EmailField()
   phone = PhoneNumberField(null=False, blank=False, unique=True)
   address = models.TextField()
   website = models.TextField()
   other_contact_info = models.TextField()
   preferred_vendor = models.BooleanField()


# Inventory order management
class Orders(models.Model):
   ORDER_STATUS_CHOICES = [
      ('Pending', 'Pending'), 
      ('Received', 'Received'), 
      ('Cancelled', 'Cancelled')
   ]

   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   vendor = models.ForeignKey(Vendors, on_delete=models.PROTECT)
   inventory_item = models.ForeignKey(InventoryItems, on_delete=models.CASCADE)
   unit_price = models.DecimalField(max_digits=10, decimal_places=2)
   ordered_quantity = models.DecimalField(max_digits=10, decimal_places=2)
   total_order_value = models.DecimalField(max_digits=10, decimal_places=2)
   order_date = models.DateField()
   arrival_date = models.DateField()
   order_status = models.CharField(max_length=9, choices=ORDER_STATUS_CHOICES)

   def save(self, *args, **kwargs):
      super().save(*args, **kwargs)
      
      avg_ordered_quantity = Orders.objects.filter(
         external_location=self.external_location, 
         inventory_item=self.inventory_item
      ).aggregate(Avg('ordered_quantity'))['ordered_quantity__avg']

      if self.ordered_quantity > (avg_ordered_quantity - (avg_ordered_quantity * 0.10)):
         OrderInventoryAlerts.objects.create(
            external_location=self.external_location,
            order=self.pk,
            alert_message=f'Order quantity for order {self.pk} is more than 10% above average order quantity for this product. Double check to see if this is a mistake.',
            alert_type='Order Alert'
         )

      elif self.ordered_quantity < (avg_ordered_quantity - (avg_ordered_quantity * 0.10)):
         OrderInventoryAlerts.objects.create(
            external_location=self.external_location,
            order=self.pk,
            alert_message=f'Order quantity for order {self.pk} is more than 10% below average order quantity for this product. Double check to see if this is a mistake.',
            alert_type='Order Alert'
         )


class OrderInventory(models.Model):
   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   order = models.ForeignKey(Orders, on_delete=models.CASCADE)
   received_quantity = models.DecimalField(max_digits=10, decimal_places=3) 
   received_date = models.DateField(auto_now=True)
   quantity_variance = models.DecimalField(max_digits=10, decimal_places=3)
   quantity_variance_percent = models.DecimalField(max_digits=10, decimal_places=1)
   total_order_value_variance = models.DecimalField(max_digits=10, decimal_places=2)
   total_order_value_variance_percent = models.DecimalField(max_digits=10, decimal_places=1)

   @property
   def get_external_location(self):
      return self.order.external_location

   @property
   def calc_quantity_variance(self):
      return self.received_quantity - self.order.ordered_quantity

   @property
   def calc_quantity_variance_percent(self):
      return (self.calc_quantity_variance / self.order.ordered_quantity) * 100
   
   @property
   def calc_total_order_value_variance(self):
      avg_unit_price = self.order.total_order_value / self.order.ordered_quantity
      actual_total_order_value = self.received_quantity * avg_unit_price
      
      return actual_total_order_value - self.order.total_order_value

   @property
   def calc_total_order_value_variance_percent(self):
      return (self.calc_total_order_value_variance / self.order.total_order_value) * 100

   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      self.quantity_variance = self.calc_quantity_variance
      self.quantity_variance_percent = self.calc_quantity_variance_percent
      self.total_order_value_variance = self.calc_total_order_value_variance
      self.total_order_value_variance_percent = self.calc_total_order_value_variance_percent

      super().save(*args, **kwargs)

      inventory_item = InventoryItems.objects.get(pk=self.order.inventory_item)
      inventory_item.quantity += self.received_quantity
      inventory_item.total_value += (self.received_quantity * self.order.unit_price)
      inventory_item.save()

      if self.quantity_variance_percent >= 5:
         location_training_insights = LocationTrainingInsights.objects.get(
            external_location=self.order.external_location
         )

         if not location_training_insights:
            LocationTrainingInsights.objects.create(
               external_location=self.order.external_location,
               variance_faults=1,
               suggested_training='TBC', # Use KeplerPro to generate suggestions
            )
         else:
            location_training_insights.variance_faults += 1
            location_training_insights.suggested_training = 'TBC' # Use KeplerPro to generate suggestions
            location_training_insights.save()


      if self.quantity_variance > 0:
         OrderInventoryAlerts.objects.create(
            external_location=self.external_location,
            order=self.order,
            alert_message=f'The quantity variance for order {self.order} is {self.quantity_variance_percent}% and the total order value variance is ${self.total_order_value_variance}.',
            alert_type='Quantity Variance'
         )
      
      if self.total_order_value_variance > 0:
         OrderInventoryAlerts.objects.create(
            external_location=self.external_location,
            order=self.order,
            alert_message=f'The total order value variance for order {self.order} is ${self.total_order_value_variance}.',
            alert_type='Total Order Value Variance'
         )
      
      if self.received_date > self.order.arrival_date:
         OrderInventoryAlerts.objects.create(
            external_location=self.external_location,
            order=self.order,
            alert_message=f'The arrival date for order {self.order} is {self.received_date} and the expected arrival date is {self.order.arrival_date}.',
            alert_type='Arrival Date Variance'
         )


class OrderInventoryAlerts(models.Model):
   ALERT_TYPE_CHOICES = [
      ('Quantity Variance', 'Quantity Variance'), 
      ('Value Variance', 'Value Variance'), 
      ('Arrival Date Variance', 'Arrival Date Variance'), 
      ('Order Alert', 'Order Alert')
   ]

   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   order = models.ForeignKey(Orders, on_delete=models.CASCADE)
   alert_message = models.TextField()
   alert_date = models.DateField(auto_now_add=True)
   alert_type = models.CharField(max_length=21, choices=ALERT_TYPE_CHOICES)

   @property
   def vendor(self):
      return self.order.vendor


# Task management 
class Tasks(models.Model):
   TASK_TYPE_CHOICES = [
      ('Staff-related', 'Staff-related'), 
      ('Menu-related', 'Menu-related'), 
      ('Recipe-related', 'Recipe-related'), 
      ('Inventory-related', 'Inventory-related'), 
      ('Kitchen-related', 'Kitchen-related'), 
      ('Dining room-related', 'Dining room-related'), 
      ('Bathroom-related', 'Bathroom-related'), 
      ('Building-related', 'Building-related'), 
      ('Other', 'Other')
   ]

   PRIORITY_CHOICES = [
      ('Low', 'Low'), 
      ('Medium', 'Medium'), 
      ('High', 'High')
   ]

   STATUS_CHOICES = [
      ('Pending', 'Pending'),
      ('In Progress', 'In Progress'), 
      ('Completed', 'Completed'),
   ]

   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   task_name = models.TextField()
   description = models.TextField()
   task_type = models.CharField(max_length=19, choices=TASK_TYPE_CHOICES)
   due_date = models.DateTimeField()
   employee_assignee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='employee_assignee')
   priority = models.CharField(max_length=7, choices=PRIORITY_CHOICES)
   status = models.CharField(max_length=11, choices=STATUS_CHOICES, default='Pending')
   employee_assignor = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='employee_assignor')

   @property
   def get_external_location(self):
      return self.employee_assignee.external_location

   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      super().save(*args, **kwargs)


class TaskComments(models.Model):
   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
   employee_tasker = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='employee_tasker')
   comment = models.TextField()
   comment_date = models.DateTimeField(auto_now_add=True)
   employee_commenter = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='employee_commenter')

   @property
   def get_external_location(self):
      return self.task.external_location

   @property
   def get_employee_tasker(self):
      return self.task.employee_assignee
   
   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      self.employee_tasker = self.get_employee_tasker

      super().save(*args, **kwargs)


class TaskAlerts(models.Model):
   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
   employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
   alert_message = models.TextField()
   alert_date = models.DateTimeField(auto_now_add=True)

   @property
   def get_external_location(self):
      return task.external_location

   @property
   def get_employee(self):
      return task.employee_assignee

   @property
   def get_alert_message(self):
      if self.alert_date - self.task.due_date < timedelta(days=1):
         if (self.alert_date - self.task.due_date < timedelta(hours=5)):
            return f'Your task, "{self.task.task_name}," is due in {self.alert_date - self.task.due_date.strftime("%H:%M")}!'

         return f'Your task, "{self.task.task_name}," is due today!'

      elif self.alert_date - self.task.due_date < timedelta(days=2):
         return f'Your task, "{self.task.task_name}," is due tomorrow!'
      elif self.alert_date - self.task.due_date < timedelta(days=3):
         return f'Your task, "{self.task.task_name}," is due in 2 days!'
      else:
         return f'Your task, "{self.task.task_name}," is due in {self.task.due_date.strftime("%B %d, %Y")}!'

   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      self.employee = self.get_employee
      self.alert_message = self.get_alert_message

      super().save(*args, **kwargs)


# Recipe management
class Recipes(models.Model):
   region_location = models.ForeignKey(RegionLocations, null=True, blank=True, on_delete=models.CASCADE)

   recipe_name = models.CharField(max_length=100)
   image = models.ImageField(upload_to='images/')
   description = models.TextField()
   preparation_time = models.DecimalField(max_digits=10, decimal_places=1)
   cooking_temperature = models.PositiveIntegerField()
   cooking_time = models.DecimalField(max_digits=10, decimal_places=1)
   dishing_up_time = models.DecimalField(max_digits=10, decimal_places=1)
   total_recipe_time = models.DecimalField(max_digits=10, decimal_places=1)
   quality_standards = models.TextField()
   serving_size = models.DecimalField(max_digits=10, decimal_places=3)

   @property
   def calc_total_recipe_time(self):
      return self.preparation_time + self.cooking_time + self.dishing_up_time

   @property
   def ingredients(self):
      recipe_ingredients = RecipeIngredients.objects.filter(recipe=self.pk)
      ingredients = {}

      for ingredient in recipe_ingredients:
         ingredients[ingredient.inventory_item.item_name] = ingredient.quantity
      
      return ingredients

   @property
   def ingredient_costs(self):
      recipe_ingredients = RecipeIngredients.objects.filter(recipe=self.pk)
      ingredient_costs = 0

      for ingredient in recipe_ingredients:
         ingredient_costs += ingredient.inventory_item.avg_unit_price * ingredient.quantity
      
      return ingredient_costs

   def save(self, *args, **kwargs):
      self.total_recipe_time = self.calc_total_recipe_time
      super().save(*args, **kwargs)


class RecipeIngredients(models.Model):
   region_location = models.ForeignKey(RegionLocations, null=True, blank=True, on_delete=models.CASCADE)

   recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
   inventory_item = models.ForeignKey(InventoryItems, on_delete=models.CASCADE)
   quantity = models.DecimalField(max_digits=10, decimal_places=3)

   @property
   def get_region_location(self):
      return recipe.region_location
   
   def save(self, *args, **kwargs):
      self.region_location = self.get_region_location
      super().save(*args, **kwargs)


# Menu management
class MenuItems(models.Model):
   COURSE_CHOICES = [
      ('Appetizer', 'Appetizer'), 
      ('Entrée', 'Entrée'), 
      ('Dessert', 'Dessert')
   ]

   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
   item_name = models.CharField(max_length=100)
   image = models.ImageField(upload_to='images/')
   price = models.DecimalField(max_digits=10, decimal_places=2)
   course = models.CharField(max_length=9, choices=COURSE_CHOICES)
   is_available = models.BooleanField()
   gross_profit = models.DecimalField(max_digits=10, decimal_places=2)

   @property
   def calc_gross_profit(self):
      return self.price - self.recipe.ingredient_costs

   def save(self, *args, **kwargs):
      self.gross_profit = self.calc_gross_profit
      super().save(*args, **kwargs)


class AddOns(models.Model):
   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   inventory_item = models.ForeignKey(InventoryItems, on_delete=models.CASCADE)
   add_on_name = models.TextField()
   additional_quantity = models.DecimalField(max_digits=10, decimal_places=3)
   additional_price = models.DecimalField(max_digits=10, decimal_places=2)
   is_available = models.BooleanField()
   additional_ingredient_costs = models.DecimalField(max_digits=10, decimal_places=2)

   @property
   def get_external_location(self):
      return self.inventory_item.external_location

   @property
   def calc_additional_ingredient_costs(self):
      return self.additional_quantity * self.inventory_item.avg_unit_price

   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      self.additional_ingredient_costs = self.calc_additional_ingredient_costs
      self.add_on_name = 'Extra ' + self.add_on_name

      super().save(*args, **kwargs)


class MenuItemAddOns(models.Model):
   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   menu_item = models.ForeignKey(MenuItems, on_delete=models.CASCADE)
   add_on = models.ForeignKey(AddOns, on_delete=models.CASCADE)

   @property
   def get_external_location(self):
      return self.menu_item.external_location

   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      super().save(*args, **kwargs)


class MenuItemOrders(models.Model):
   ORDER_STATUS_CHOICES = [
      ('Pending', 'Pending'), 
      ('In Progress', 'In Progress'), 
      ('Completed', 'Completed'), 
      ('Recalled', 'Recalled')
   ]

   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   menu_item = models.ForeignKey(MenuItems, on_delete=models.CASCADE)
   add_ons = models.ManyToManyField(AddOns, blank=True)
   quantity = models.PositiveIntegerField(default=1)
   order_time = models.TimeField(auto_now_add=True)
   internal_location = models.ForeignKey(InternalLocations, on_delete=models.CASCADE)
   order_status = models.CharField(max_length=11, choices=ORDER_STATUS_CHOICES, default='Pending')

   @property
   def get_external_location(self):
      return menu_item.external_location

   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      super().save(*args, **kwargs)

      if self.order_status == 'In Progress':
         recipe = self.menu_item.recipe
         recipe_ingredients = RecipeIngredients.objects.filter(recipe=recipe)

         for ingredient in recipe_ingredients:
            inventory_item = InventoryItems.objects.get(id=ingredient.inventory_item)
            inventory_item.quantity -= ingredient.quantity * self.quantity
            inventory_item.total_value -= (ingredient.quantity * ingredient.inventory_item.avg_unit_price) * self.quantity
            inventory_item.save()
         
         if self.add_ons.exists():
            for add_on in self.add_ons.all():
               add_on_inventory_item = InventoryItems.objects.get(id=add_on.inventory_item.id)
               add_on_inventory_item.quantity -= add_on.additional_quantity * self.quantity
               add_on_inventory_item.total_value -= add_on.additional_ingredient_costs * self.quantity
               add_on_inventory_item.save()


class MenuEngineeringReports(models.Model):
   MATRIX_CHOICES = [
      ('Star', 'Star'),
      ('Puzzle', 'Puzzle'),
      ('Plow horse', 'Plow horse'),
      ('Dog', 'Dog'),
      ('Insufficient data', 'Insufficient data')
   ]

   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   menu_item = models.ForeignKey(MenuItems, on_delete=models.CASCADE)
   total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
   total_cogs = models.DecimalField(max_digits=10, decimal_places=2)
   gross_profit = models.DecimalField(max_digits=10, decimal_places=2)
   number_sold = models.PositiveIntegerField()
   matrix = models.CharField(max_length=17, choices=MATRIX_CHOICES)
   report_date = models.DateField(auto_now_add=True)

   @property
   def get_external_location(self):
      return menu_item.external_location

   @property
   def calc_total_revenue(self):
      menu_item_orders_payments = list(Payments.objects.filter(
         external_location=self.external_location
      ).values_list('ordered_menu_items_and_quantities', flat=True))

      if len(menu_item_orders_payments) == 0:
         return 0

      total_revenue = 0.0

      for menu_item_orders_payment in menu_item_orders_payments:

         for menu_item, info in menu_item_orders_payment.items():
            if self.menu_item == menu_item:
               total_plate_price = 0.0

               menu_item = MenuItems.objects.get(pk=menu_item)
               total_plate_price += menu_item.price * info['quantity']

               for add_on in info['add-ons']:
                  add_on = AddOns.objects.get(pk=add_on)
                  total_plate_price += add_on.additional_price * info['quantity']

               total_revenue += total_plate_price

      return total_revenue

   @property
   def calc_total_cogs(self):
      menu_item_orders_payments = list(Payments.objects.filter(
         external_location=self.external_location
      ).values_list('ordered_menu_items_and_quantities', flat=True))

      if len(menu_item_orders_payments) == 0:
         return 0

      total_cogs = 0.0

      for menu_item_orders_payment in menu_item_orders_payments:

         for menu_item, info in menu_item_orders_payment.items():
            if self.menu_item == menu_item:
               total_plate_cost = 0.0

               menu_item = MenuItems.objects.get(pk=menu_item)
               total_plate_cost += menu_item.recipe.ingredient_costs * info['quantity']

               for add_on in info['add-ons']:
                  add_on = AddOns.objects.get(pk=add_on)
                  total_plate_cost += add_on.additional_ingredient_costs * info['quantity']
               
               total_cogs += total_plate_cost
      
      return total_cogs

   @property
   def calc_gross_profit(self):
      return self.calc_total_revenue - self.calc_total_cogs

   @property
   def calc_number_sold(self):
      menu_item_orders_payments = list(Payments.objects.filter(
         external_location=self.external_location
      ).values_list('ordered_menu_items_and_quantities', flat=True))

      if len(menu_item_orders_payments) == 0:
         return 0

      number_sold = 0

      for menu_item_orders_payment in menu_item_orders_payments:

         for menu_item, info in menu_item_orders_payment.items():
            if self.menu_item == menu_item:
               number_sold += info['quantity']
      
      return number_sold

   @property
   def get_matrix(self):
      avg_number_sold = MenuEngineeringReports.objects.filter(
         external_location=self.external_location
      ).exclude(menu_item=self.menu_item).aggregate(Avg('number_sold'))['number_sold__avg'] or 0

      avg_gross_profit = MenuEngineeringReports.objects.filter(
         external_location=self.external_location
      ).exclude(menu_item=self.menu_item).aggregate(Avg('gross_profit'))['gross_profit__avg'] or 0

      if self.calc_number_sold > avg_number_sold and self.calc_gross_profit > avg_gross_profit:
         return 'Star'
      elif self.calc_number_sold < avg_number_sold and self.calc_gross_profit > avg_gross_profit:
         return 'Puzzle' 
      elif self.calc_number_sold > avg_number_sold and self.calc_gross_profit < avg_gross_profit:
         return 'Plow Horse'
      elif self.calc_number_sold < avg_number_sold and self.calc_gross_profit < avg_gross_profit:
         return 'Dog'
      else:
         return 'Insufficient Data'

   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      self.total_revenue = self.calc_total_revenue
      self.total_cogs = self.calc_total_cogs
      self.gross_profit = self.calc_gross_profit
      self.number_sold = self.calc_number_sold
      self.matrix = self.get_matrix

      super().save(*args, **kwargs)


# Menu waste management
class WasteRecords(models.Model):
   WASTE_REASON_CHOICES = [
      ('Overproduction/Large portion size', 'Overproduction/Large portion size'), 
      ('Spoilage', 'Spoilage'), 
      ('Over-ordering', 'Over-ordering')
   ]

   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)
   
   menu_item = models.ForeignKey(MenuItems, on_delete=models.CASCADE)
   weight_wasted = models.DecimalField(max_digits=10, decimal_places=3)
   waste_reason = models.CharField(max_length=33, choices=WASTE_REASON_CHOICES)
   date_wasted = models.DateField(auto_now=True)

   @property
   def get_external_location(self):
      return menu_item.external_location

   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      super().save(*args, **kwargs)


class WasteAnalysis(models.Model):
   MOST_COMMON_WASTE_REASON_CHOICES = [
      ('Overproduction/Large portion size', 'Overproduction/Large portion size'), 
      ('Spoilage', 'Spoilage'), 
      ('Over-ordering', 'Over-ordering')
   ]

   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   menu_item = models.ForeignKey(MenuItems, on_delete=models.CASCADE)
   total_weight_wasted = models.DecimalField(max_digits=10, decimal_places=2)
   most_common_waste_reason = models.CharField(max_length=33, choices=MOST_COMMON_WASTE_REASON_CHOICES)
   analysis_date = models.DateField(auto_now_add=True)

   @property
   def get_external_location(self):
      return menu_item.external_location

   @property
   def get_total_weight_wasted(self):
      return WasteRecords.objects.filter(
         menu_item=self.menu_item
      ).aggregate(Sum('weight_wasted'))['weight_wasted__sum'] or 0

   @property
   def get_most_common_waste_reason(self):
      return WasteRecords.objects.filter(
         menu_item=self.menu_item
      ).values_list('waste_reason', flat=True).annotate(Count('waste_reason')).order_by('-waste_reason__count')[0] or "Insufficient data"

   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      self.total_weight_wasted = self.get_total_weight_wasted
      self.most_common_waste_reason = self.get_most_common_waste_reason

      super().save(*args, **kwargs)


# Receipt creator + transactions log/tracker
class Payments(models.Model):
   CATEGORY_CHOICES = [
      ('Dine-in', 'Dine-in'), 
      ('Takeout', 'Takeout'), 
      ('Delivery', 'Delivery')
   ]

   PAYMENT_TYPE_CHOICES = [
      ('Cash', 'Cash'), 
      ('Credit/Debit', 'Credit/Debit'), 
      ('Gift card', 'Gift card'), 
      ('Cryptocurrency', 'Cryptocurrency'), 
      ('Other', 'Other')
   ]

   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   internal_location = models.ForeignKey(InternalLocations, on_delete=models.CASCADE)
   ordered_menu_items_and_quantities = models.JSONField()
   name_ordered_menu_items_and_quantities = models.JSONField()
   tip_amount_percent = models.PositiveIntegerField(default=0)
   service_charge_percent = models.PositiveIntegerField(default=0)
   total_bill = models.DecimalField(max_digits=10, decimal_places=2)
   employee = models.ForeignKey(Employees, null=True, blank=True, on_delete=models.SET_NULL)
   category = models.CharField(max_length=8, choices=CATEGORY_CHOICES)
   payment_type = models.CharField(max_length=14, choices=PAYMENT_TYPE_CHOICES)
   payment_datetime = models.DateTimeField(auto_now_add=True)

   @property
   def get_external_location(self):
      return self.internal_location.external_location

   @property
   def get_ordered_menu_items_and_quantities(self):
      menu_item_orders_at_location = MenuItemOrders.objects.filter(
         internal_location=self.internal_location, 
         external_location=self.get_external_location, 
         order_status='Completed'
      )

      ordered_menu_items_and_quantities = {}

      for menu_item_order in menu_item_orders_at_location:
         orderded_menu_items_and_quantities[menu_item_order.menu_item] = {
            'quantity': menu_item_order.quantity,
            'add-ons': [add_on.pk for add_on in menu_item_order.add_ons.all()]
         }
      
      return ordered_menu_items_and_quantities

   @property
   def get_name_ordered_menu_items_and_quantities(self):
      name_menu_items_and_quantities = {}

      for menu_item, info in self.get_ordered_menu_items_and_quantities.items():
         menu_item = MenuItems.objects.get(pk=menu_item)

         name_menu_items_and_quantities[menu_item.item_name] = {
            'quantity': info['quantity'],
            'add-ons': [AddOns.objects.get(pk=add_on).add_on_name for add_on in info['add-ons']]
         }

      return name_menu_items_and_quantities

   @property
   def calc_total_bill(self):
      total_bill = 0
      
      for menu_item, info in self.get_ordered_menu_items_and_quantities.items():
         menu_item = MenuItems.objects.get(pk=menu_item)
         total_bill += menu_item.price * info['quantity']

         for add_on in info['add-ons']:
            add_on = AddOns.objects.get(pk=add_on)
            total_bill += add_on.additional_price * info['quantity']

      return (
         total_bill 
         + (total_bill * (self.tip_amount_percent / 100)) 
         + (total_bill * (self.service_charge_percent / 100))
      )

   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      self.ordered_menu_items_and_quantities = self.get_ordered_menu_items_and_quantities
      self.name_ordered_menu_items_and_quantities = self.get_name_ordered_menu_items_and_quantities
      self.total_bill = self.calc_total_bill

      super().save(*args, **kwargs)

      menu_item_orders_at_location = MenuItemOrders.objects.filter(
         internal_location=self.internal_location, 
         external_location=self.external_location, 
         order_status='Completed'
      ).delete()

      tip_amount = (
         abs((self.total_bill * (self.tip_amount_percent / 100)) 
         - (self.total_bill * (self.service_charge_percent / 100)))
      )

      employee_performance = EmployeesPerformance.objects.get_or_create(employee=self.employee)
      employee_performance.total_tips_received += tip_amount
      employee_performance.total_transactions_completed += 1
      employee_performance.total_sales_handled_amount += self.total_bill
      employee_performance.save()

      EmployeeTipRecords.objects.create(
         external_location=self.external_location,
         employee=self.employee,
         category=self.category,
         internal_location=self.internal_location,
         tip_amount=tip_amount,
         tip_type=self.payment_type,
         daily_shift_record=DailyShiftRecords.objects.filter(
            external_location=self.external_location,
            employee=self.employee,
            shift_date=self.payment_datetime,
            punch_in_time__isnull=False,
            punch_out_time__isnull=True
         ).pk,
      )


# Nutrition and allergen management
class NutritionAllergenInfo(models.Model):
   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   menu_item = models.ForeignKey(MenuItems, on_delete=models.CASCADE)
   serving_size = models.DecimalField(max_digits=10, decimal_places=3)
   calories = models.PositiveIntegerField()
   total_fat = models.DecimalField(max_digits=10, decimal_places=1)
   saturated_fat = models.DecimalField(max_digits=10, decimal_places=1)
   trans_fat = models.DecimalField(max_digits=10, decimal_places=1)
   cholesterol = models.PositiveIntegerField()
   sodium = models.PositiveIntegerField()
   total_carbohydrates = models.PositiveIntegerField()
   dietary_fiber = models.PositiveIntegerField()
   total_sugars = models.PositiveIntegerField()
   added_sugars = models.PositiveIntegerField()
   protein = models.PositiveIntegerField()
   vitamin_d = models.PositiveIntegerField()
   calcium = models.PositiveIntegerField()
   iron = models.PositiveIntegerField()
   potassium = models.PositiveIntegerField()
   allergens = models.TextField()

   @property
   def get_external_location(self):
      return self.menu_item.external_location

   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      super().save(*args, **kwargs)


# Inventory cost reports
class AccountingPeriods(models.Model):
   region_location = models.ForeignKey(RegionLocations, null=True, blank=True, on_delete=models.CASCADE)

   accounting_period_start = models.DateField()
   accounting_period_end = models.DateField()
   added_date = models.DateTimeField(auto_now_add=True)


class InventoryCostReports(models.Model):
   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   accounting_period = models.ForeignKey(AccountingPeriods, null=True, blank=True, on_delete=models.SET_NULL)
   beginning_inventory = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
   ending_inventory = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
   purchases = models.DecimalField(max_digits=10, decimal_places=3)
   total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
   total_inventory_wastage_value = models.DecimalField(max_digits=10, decimal_places=2)
   theoretical_cogs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   actual_cogs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   current_cogs = models.DecimalField(max_digits=10, decimal_places=2)
   cogs_variance = models.DecimalField(max_digits=10, decimal_places=2)
   cogs_variance_percent = models.DecimalField(max_digits=10, decimal_places=1)
   theoretical_gross_profit = models.DecimalField(max_digits=10, decimal_places=2)
   actual_gross_profit = models.DecimalField(max_digits=10, decimal_places=2)
   total_transfers = models.PositiveIntegerField()
   report_date = models.DateField(auto_now_add=True)

   @property
   def get_accounting_period(self):
      return AccountingPeriods.objects.filter(
         accounting_period_start__lte=self.report_date, 
         accounting_period_end__gte=self.report_date
      ).first()

   @property
   def get_beginning_inventory(self):
      previous_accounting_period_report = InventoryCostReports.objects.filter(
         accounting_period__lt=self.get_accounting_period,
         external_location=self.external_location
      ).order_by('-accounting_period').first()

      if previous_accounting_period_report:
         return previous_accounting_period_report.ending_inventory

      elif self.report_date == self.get_accounting_period.accounting_period_start:
         return InventoryItems.objects.filter(
            external_location=self.external_location
         ).aggregate(Sum('total_value'))['total_value__sum'] or 0

      else:
         start_of_accounting_period_report = InventoryCostReports.objects.filter(
            external_location=self.external_location,
            report_date=self.get_accounting_period.accounting_period_start
         ).first()

         if start_of_accounting_period_report:
            return start_of_accounting_period_report.beginning_inventory
         else:
            return None

   @property
   def get_ending_inventory(self):
      if self.report_date == self.get_accounting_period.accounting_period_end:
         ending_inventory = InventoryItems.objects.filter(
            external_location=self.external_location
         ).aggregate(Sum('total_value'))['total_value__sum'] or 0

         return ending_inventory
      
      return None

   @property
   def get_purchases(self):
      return Orders.objects.filter(
         external_location=self.external_location,
         order_date__range=(self.get_accounting_period.accounting_period_start, self.get_accounting_period.accounting_period_end)
      ).aggregate(Sum('total_order_value'))['total_order_value__sum'] or 0

   @property
   def get_total_revenue(self):
      return Payments.objects.filter(
         external_location=self.external_location,
         payment_datetime__range=(self.get_accounting_period.accounting_period_start, self.get_accounting_period.accounting_period_end)
      ).aggregate(Sum('total_bill'))['total_bill__sum'] or 0

   @property
   def get_total_inventory_wastage_value(self):
      return InventoryWasteBin.objects.filter(
         external_location=self.external_location,
         waste_date__range=(self.get_accounting_period.accounting_period_start, self.get_accounting_period.accounting_period_end)
      ).aggregate(Sum('money_wasted'))['money_wasted__sum'] or 0

   @property
   def calc_theoretical_cogs(self):
      if self.report_date == self.get_accounting_period.accounting_period_end:
         return (self.get_beginning_inventory + self.get_purchases) - self.get_ending_inventory
      
      return None

   @property
   def calc_actual_cogs(self):
      if self.report_date == self.get_accounting_period.accounting_period_end:
         return self.calc_theoretical_cogs + self.get_total_inventory_wastage_value
      
      return None

   @property
   def calc_current_cogs(self):
      current_inventory_value = InventoryItems.objects.filter(
         external_location=self.external_location
      ).aggregate(Sum('total_value'))['total_value__sum'] or 0

      return (
         ((self.get_beginning_inventory + self.get_purchases) 
         - current_inventory_value) 
         + self.get_total_inventory_wastage_value
      )

   @property
   def calc_cogs_variance(self):
      if self.report_date == self.get_accounting_period.accounting_period_end:
         return self.calc_actual_cogs - self.calc_theoretical_cogs

      return self.calc_current_cogs - (self.calc_current_cogs - self.get_total_inventory_wastage_value)

   @property
   def calc_cogs_variance_percent(self):
      if self.report_date == self.get_accounting_period.accounting_period_end:
         return (self.calc_cogs_variance / self.calc_theoretical_cogs) * 100
      
      return (
         (self.calc_cogs_variance 
         / (self.calc_current_cogs - self.get_total_inventory_wastage_value)) 
         * 100
      )

   @property
   def calc_theoretical_gross_profit(self):
      if self.report_date == self.get_accounting_period.accounting_period_end:
         return self.get_total_revenue - self.calc_theoretical_cogs
      
      return self.get_total_revenue - (self.calc_current_cogs - self.get_total_inventory_wastage_value)

   @property
   def calc_actual_gross_profit(self):
      if self.report_date == self.get_accounting_period.accounting_period_end:
         return self.get_total_revenue - self.calc_actual_cogs

      return self.get_total_revenue - self.calc_current_cogs

   @property
   def get_total_transfers(self):
      return InventoryTransfers.objects.filter(
         external_location=self.external_location,
         transfer_date__range=(self.get_accounting_period.accounting_period_start, self.get_accounting_period.accounting_period_end)
      ).count()

   def save(self, *args, **kwargs):
      self.accounting_period = self.get_accounting_period
      self.beginning_inventory = self.get_beginning_inventory
      self.ending_inventory = self.get_ending_inventory
      self.purchases = self.get_purchases
      self.total_revenue = self.get_total_revenue
      self.total_inventory_wastage_value = self.get_total_inventory_wastage_value
      self.theoretical_cogs = self.calc_theoretical_cogs
      self.actual_cogs = self.calc_actual_cogs
      self.current_cogs = self.calc_current_cogs
      self.cogs_variance = self.calc_cogs_variance
      self.cogs_variance_percent = self.calc_cogs_variance_percent
      self.theoretical_gross_profit = self.calc_theoretical_gross_profit
      self.actual_gross_profit = self.calc_actual_gross_profit
      self.total_transfers = self.get_total_transfers

      super().save(*args, **kwargs)

      if self.gross_profit <= 0:
         location_training_insights = LocationTrainingInsights.objects.get(
            external_location=self.external_location
         )

         if not location_training_insights:
            LocationTrainingInsights.objects.create(
               external_location=self.external_location,
               variance_faults=1,
               suggested_training='TBC', # Use KeplerPro to generate suggestions
            )
         else:
            location_training_insights.variance_faults += 1
            location_training_insights.suggested_training = 'TBC' # Use KeplerPro to generate suggestions
            location_training_insights.save()
      
      if self.cogs_variance_percent >= 10:
         location_training_insights = LocationTrainingInsights.objects.get(
            external_location=self.external_location
         )

         if not location_training_insights:
            LocationTrainingInsights.objects.create(
               external_location=self.external_location,
               variance_faults=1,
               suggested_training='TBC', # Use KeplerPro to generate suggestions
            )
         else:
            location_training_insights.variance_faults += 1
            location_training_insights.suggested_training = 'TBC' # Use KeplerPro to generate suggestions
            location_training_insights.save()


class InventoryUsage(models.Model):
   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   inventory_item = models.ForeignKey(InventoryItems, on_delete=models.CASCADE)
   accounting_period = models.ForeignKey(AccountingPeriods, null=True, blank=True, on_delete=models.SET_NULL)
   opening_stock_quantity = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
   opening_stock_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   closing_stock_quantity = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
   closing_stock_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   purchases_quantity = models.DecimalField(max_digits=10, decimal_places=3)
   purchases_value = models.DecimalField(max_digits=10, decimal_places=2)
   wasted_quantity = models.DecimalField(max_digits=10, decimal_places=3)
   wasted_value = models.DecimalField(max_digits=10, decimal_places=2)
   theoretical_usage_quantity = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
   theoretical_usage_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   actual_usage_quantity = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
   actual_usage_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   current_usage_quantity = models.DecimalField(max_digits=10, decimal_places=3)
   current_usage_value = models.DecimalField(max_digits=10, decimal_places=2)
   usage_variance = models.DecimalField(max_digits=10, decimal_places=3)
   usage_variance_percent = models.DecimalField(max_digits=10, decimal_places=1)
   report_date = models.DateField(auto_now_add=True)

   @property
   def get_external_location(self):
      return self.inventory_item.external_location

   @property
   def get_accounting_period(self):
      return AccountingPeriods.objects.filter(
         accounting_period_start__lte=self.report_date, 
         accounting_period_end__gte=self.report_date
      ).first()

   @property
   def weeks_since_accounting_start(self):
      delta = self.report_date - self.get_accounting_period.accounting_period_start
      return delta.days / 7

   @property
   def get_opening_stock_quantity(self):
      previous_accounting_period_report = InventoryUsage.objects.filter(
         accounting_period__lt=self.get_accounting_period,
         inventory_item=self.inventory_item,
         external_location=self.external_location
      ).order_by('-accounting_period').first()

      if previous_accounting_period_report:
         return previous_accounting_period_report.closing_stock_quantity

      elif self.report_date == self.get_accounting_period.accounting_period_start:
         return InventoryItems.objects.filter(
            pk=self.inventory_item,
            external_location=self.external_location
         ).aggregate(Sum('quantity'))['quantity__sum'] or 0

      else:
         start_of_accounting_period_report = InventoryUsage.objects.filter(
            external_location=self.external_location,
            inventory_item=self.inventory_item,
            report_date=self.get_accounting_period.accounting_period_start
         ).first()

         if start_of_accounting_period_report:
            return start_of_accounting_period_report.opening_stock_quantity
         else:
            None

   @property
   def get_opening_stock_value(self):
      previous_accounting_period_report = InventoryUsage.objects.filter(
         accounting_period__lt=self.get_accounting_period,
         inventory_item=self.inventory_item,
         external_location=self.external_location
      ).order_by('-accounting_period').first()

      if previous_accounting_period_report:
         return previous_accounting_period_report.closing_stock_value

      elif self.report_date == self.get_accounting_period.accounting_period_start:
         return InventoryItems.objects.filter(
            pk=self.inventory_item,
            external_location=self.external_location
         ).aggregate(Sum('total_value'))['total_value__sum'] or 0

      else:
         start_of_accounting_period_report = InventoryUsage.objects.filter(
            external_location=self.external_location,
            inventory_item=self.inventory_item,
            report_date=self.get_accounting_period.accounting_period_start
         ).first()

         if start_of_accounting_period_report:
            return start_of_accounting_period_report.opening_stock_value
         else:
            return None

   @property
   def get_closing_stock_quantity(self):
      if self.report_date == self.get_accounting_period.accounting_period_end:
         return self.inventory_item.quantity
      
      return None

   @property
   def get_closing_stock_value(self):
      if self.report_date == self.get_accounting_period.accounting_period_end:
         return self.inventory_item.total_value
      
      return None

   @property 
   def get_purchases_quantity(self):
      return Orders.objects.filter(
         external_location=self.external_location,
         inventory_item=self.inventory_item,
         order_date__range=(self.get_accounting_period.accounting_period_start, self.get_accounting_period.accounting_period_end)
      ).aggregate(Sum('ordered_quantity'))['ordered_quantity__sum'] or 0

   @property
   def get_purchases_value(self):
      return Orders.objects.filter(
         external_location=self.external_location,
         inventory_item=self.inventory_item,
         order_date__range=(self.get_accounting_period.accounting_period_start, self.get_accounting_period.accounting_period_end)
      ).aggregate(Sum('total_order_value'))['total_order_value__sum'] or 0

   @property
   def get_wasted_quantity(self):
      return InventoryWasteBin.objects.filter(
         inventory_item=self.inventory_item,
         external_location=self.external_location,
         waste_date__range=(self.get_accounting_period.accounting_period_start, self.get_accounting_period.accounting_period_end)
      ).aggregate(Sum('quantity_wasted'))['quantity_wasted__sum'] or 0

   @property
   def get_wasted_value(self):
      return InventoryWasteBin.objects.filter(
         inventory_item=self.inventory_item,
         external_location=self.external_location,
         waste_date__range=(self.get_accounting_period.accounting_period_start, self.get_accounting_period.accounting_period_end)
      ).aggregate(Sum('money_wasted'))['money_wasted__sum'] or 0

   @property
   def calc_theoretical_usage_quantity(self):
      if self.report_date == self.get_accounting_period.accounting_period_end:
         return (self.get_opening_stock_quantity + self.get_purchases_quantity) - self.get_closing_stock_quantity
      
      return None
   
   @property
   def calc_theoretical_usage_value(self):
      if self.report_date == self.get_accounting_period.accounting_period_end:
         return (self.get_opening_stock_value + self.get_purchases_value) - self.get_closing_stock_value

      return None

   @property
   def calc_actual_usage_quantity(self):
      if self.report_date == self.get_accounting_period.accounting_period_end:
         return self.calc_theoretical_usage_quantity + self.get_wasted_quantity
      
      return None

   @property
   def calc_actual_usage_value(self):
      if self.report_date == self.get_accounting_period.accounting_period_end:
         return self.calc_theoretical_usage_value + self.get_wasted_value

      return None

   @property
   def calc_current_usage_quantity(self):
      current_inventory_quantity = self.inventory_item.quantity
      return (
         ((self.get_opening_stock_quantity + self.get_purchases_quantity) 
         - current_inventory_quantity) 
         + self.get_wasted_quantity
      )

   @property
   def calc_current_usage_value(self):
      current_inventory_value = self.inventory_item.total_value
      return (
         ((self.get_opening_stock_value + self.get_purchases_value) 
         - current_inventory_value) 
         + self.get_wasted_value
      )

   @property
   def calc_usage_variance(self):
      if self.report_date == self.get_accounting_period.accounting_period_end:
         return self.calc_actual_usage_quantity - self.calc_theoretical_usage_quantity
      
      return self.calc_current_usage_quantity - (self.calc_current_usage_quantity - self.get_wasted_quantity)

   @property
   def calc_usage_variance_percent(self):
      if self.report_date == self.get_accounting_period.accounting_period_end:
         return (self.calc_usage_variance / self.calc_theoretical_usage_quantity) * 100
      
      return (
         (self.calc_usage_variance / (self.calc_current_usage_quantity 
         - self.get_wasted_quantity)) 
         * 100
      )

   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      self.accounting_period = self.get_accounting_period
      self.opening_stock_quantity = self.get_opening_stock_quantity
      self.opening_stock_value = self.get_opening_stock_value
      self.closing_stock_quantity = self.get_closing_stock_quantity
      self.closing_stock_value = self.get_closing_stock_value
      self.purchases_quantity = self.get_purchases_quantity
      self.purchases_value = self.get_purchases_value
      self.wasted_quantity = self.get_wasted_quantity
      self.wasted_value = self.get_wasted_value
      self.theoretical_usage_quantity = self.calc_theoretical_usage_quantity
      self.theoretical_usage_value = self.calc_theoretical_usage_value
      self.actual_usage_quantity = self.calc_actual_usage_quantity
      self.actual_usage_value = self.calc_actual_usage_value
      self.current_usage_quantity = self.calc_current_usage_quantity
      self.current_usage_value = self.calc_current_usage_value
      self.usage_variance = self.calc_usage_variance
      self.usage_variance_percent = self.calc_usage_variance_percent

      super().save(*args, **kwargs)

      if (self.report_date.weekday() == self.accounting_period.accounting_period_start.weekday()) and self.weeks_since_accounting_start >= 1:
         if self.weeks_since_accounting_start % 1 == 0:
            weekly_inventory_usage = self.current_usage_quantity / self.weeks_since_accounting_start
            safety_stock = self.inventory_item.safety_stock
            deliveries_per_week = self.inventory_item.deliveries_per_week
   
            par_level = round((weekly_inventory_usage + safety_stock) / deliveries_per_week, 3)
            self.inventory_item.par_level = par_level
            self.inventory_item.save()


      if self.usage_variance_percent >= 10:
         location_training_insights = LocationTrainingInsights.objects.get(
            external_location=self.external_location
         )

         if not location_training_insights:
            LocationTrainingInsights.objects.create(
               external_location=self.external_location,
               variance_faults=1,
               suggested_training='TBC', # Use KeplerPro to generate suggestions
            )
         else:
            location_training_insights.variance_faults += 1
            location_training_insights.suggested_training = 'TBC' # Use KeplerPro to generate suggestions
            location_training_insights.save()

   
class InventoryTransfers(models.Model):
   source_external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE, related_name='source_external_location')
   destination_external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE, related_name='destination_external_location')

   inventory_item = models.ForeignKey(InventoryItems, on_delete=models.CASCADE)
   quantity_transferred = models.DecimalField(max_digits=10, decimal_places=3)
   transfer_cost = models.DecimalField(max_digits=10, decimal_places=2)
   transfer_date = models.DateField()

   def save(self, *args, **kwargs):
      super().save(*args, **kwargs)

      InventoryTransfersInternal.objects.create(
         source_external_location=self.source_external_location,
         destination_external_location=self.destination_external_location,
         inventory_transfer=self.pk
      )

      inventory_item.quantity -= self.quantity_transferred
      
      inventory_item_at_destination_external_location = InventoryItems.objects.get(
         external_location=destination_external_location,
         item_name=inventory_item.item_name,
         item_type=inventory_item.item_type
      )
      inventory_item_at_destination_external_location.quantity += self.quantity_transferred

      inventory_item.save()
      inventory_item_at_destination_external_location.save()


class InventoryTransfersInternal(models.Model):
   source_external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE, related_name='source_external_location_internal')
   destination_external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE, related_name='destination_external_location_internal')

   inventory_transfer = models.ForeignKey(InventoryTransfers, on_delete=models.CASCADE)
   source_internal_location = models.ForeignKey(InternalLocations, on_delete=models.CASCADE, related_name='source_internal_location')
   destination_internal_location = models.ForeignKey(InternalLocations, on_delete=models.CASCADE, related_name='destination_internal_location')


class InventoryWasteBin(models.Model):
   WASTE_REASON_CHOICES = [
      ('Spoilage', 'Spoilage'), 
      ('Breakage', 'Breakage'), 
      ('Theft', 'Theft'), 
      ('Equipment malfunction/Faulty storage', 'Equipment malfunction/Faulty storage')
   ]

   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   inventory_item = models.ForeignKey(InventoryItems, on_delete=models.CASCADE)
   quantity_wasted = models.DecimalField(max_digits=10, decimal_places=3)
   money_wasted = models.DecimalField(max_digits=10, decimal_places=2)
   waste_reason = models.CharField(max_length=36, choices=WASTE_REASON_CHOICES)
   waste_date = models.DateField(auto_now=True)
   employee_culprit = models.ForeignKey(Employees, null=True, blank=True, on_delete=models.CASCADE, related_name='employee_culprit')
   employee_reporter = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='employee_reporter')
   comments = models.TextField()

   @property
   def get_external_location(self):
      return self.inventory_item.external_location

   @property
   def calc_money_wasted(self):
      return self.inventory_item.avg_unit_price * self.quantity_wasted

   def save(self, *args, **kwargs):
      self.external_location = self.get_external_location
      self.money_wasted = self.calc_money_wasted
      super().save(*args, **kwargs)

      inventory_item = InventoryItems.objects.get(pk=self.inventory_item)
      inventory_item.quantity -= self.quantity_wasted
      inventory_item.total_value -= self.money_wasted
      inventory_item.save()

      employee_performance = EmployeesPerformance.objects.get_or_create(employee=self.employee_culprit)
      employee_performance.total_inventory_waste_count += 1
      employee_performance.save()

      if self.waste_reason == 'Theft':
         location_training_insights = LocationTrainingInsights.objects.get(
            external_location=self.external_location
         )

         if not location_training_insights:
            LocationTrainingInsights.objects.create(
               external_location=self.external_location,
               variance_faults=1,
               suggested_training='TBC', # Use KeplerPro to generate suggestions
            )
         else:
            location_training_insights.variance_faults += 1
            location_training_insights.suggested_training = 'TBC' # Use KeplerPro to generate suggestions
            location_training_insights.save()


# Tip management
class EmployeeTipRecords(models.Model):
   CATEGORY_CHOICES = [
      ('Dine-in', 'Dine-in'), 
      ('Takeout', 'Takeout'), 
      ('Delivery', 'Delivery'), 
      ('Other', 'Other')
   ]

   TIP_TYPE_CHOICES = [
      ('Cash', 'Cash'), 
      ('Credit/Debit', 'Credit/Debit'), 
      ('Gift card', 'Gift card'), 
      ('Cryptocurrency', 'Cryptocurrency'),
      ('Other', 'Other')
   ]

   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
   category = models.CharField(max_length=8, choices=CATEGORY_CHOICES)
   internal_location = models.ForeignKey(InternalLocations, on_delete=models.CASCADE)
   tip_amount = models.DecimalField(max_digits=10, decimal_places=2)
   tip_type = models.CharField(max_length=14, choices=TIP_TYPE_CHOICES)
   tip_date = models.DateTimeField(auto_now_add=True)
   daily_shift_record = models.ForeignKey(DailyShiftRecords, on_delete=models.CASCADE)


class TipPoolingRecords(models.Model):
   CALCULATE_OR_SEND_TIPS_CHOICES = [
      ('calculate', 'Calculate Today\'s Tips'), 
      ('send', 'Send Today\'s Tips to Employees')
   ]

   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   date = models.DateField()
   calculate_or_send_tips = models.CharField(max_length=36, choices=CALCULATE_OR_SEND_TIPS_CHOICES)
   total_pool = models.DecimalField(max_digits=10, decimal_places=2)
   participants = models.TextField()
   total_hours_worked = models.DecimalField(max_digits=10, decimal_places=2)
   tip_per_hour = models.DecimalField(max_digits=10, decimal_places=2)

   @property
   def get_total_pool(self):
      return sum(EmployeeTipRecords.objects.filter(
         external_location=self.external_location, 
         tip_date=self.date
      ).values_list('tip_amount', flat=True))

   @property
   def get_participants(self):
      return list(EmployeeTipRecords.objects.filter(
         external_location=self.external_location, 
         tip_date=self.date
      ).values_list('employee', flat=True).distinct())

   @property
   def get_total_hours_worked(self):
      return sum(DailyShiftRecords.objects.filter(
         external_location=self.external_location, 
         employee__in=self.participants, 
         shift_date=self.date
      ).values_list('total_hours_worked', flat=True))

   @property
   def calc_tip_per_hour(self):
      if self.total_hours_worked > 0:
         return self.total_pool / self.total_hours_worked
      
      return 0

   def save(self, *args, **kwargs):
      self.total_pool = self.get_total_pool
      self.participants = self.get_participants
      self.total_hours_worked = self.get_total_hours_worked
      self.tip_per_hour = self.calc_tip_per_hour

      super().save(*args, **kwargs)

      if self.calculate_or_send_tips == 'send':
         for employee in self.participants:
            EmployeeTipPayouts.objects.create(
               external_location=self.external_location, 
               employee=employee, 
               tip_pool_record=self.pk
            )

   
class EmployeeTipPayouts(models.Model):
   external_location = models.ForeignKey(ExternalLocations, null=True, blank=True, on_delete=models.CASCADE)

   employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
   tip_pool_record = models.ForeignKey(TipPoolingRecords, on_delete=models.CASCADE)
   payout_amount = models.DecimalField(max_digits=10, decimal_places=2)
   tip_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
   date = models.DateField(auto_now_add=True)

   @property
   def get_tip_per_hour(self):
      return self.tip_pool_record.tip_per_hour

   @property
   def get_payout_amount(self):
      return self.get_tip_per_hour * sum(DailyShiftRecords.objects.filter(
         external_location=self.external_location, 
         employee=self.employee, 
         shift_date=self.date
      ).values_list('total_hours_worked', flat=True))

   def save(self, *args, **kwargs):
      self.payout_amount = self.get_payout_amount
      self.tip_per_hour = self.get_tip_per_hour

      super().save(*args, **kwargs)
