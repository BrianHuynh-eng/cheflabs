from django.urls import path, include
from . import views


urlpatterns = [
    # User signup + authentication
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('verify-signup/', views.VerifySignUpView.as_view(), name='verify_signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('verify-login/', views.VerifyLoginView.as_view(), name='verify_login'),
    path('logout/', views.logout_request, name='logout'),

    # Home
    path('home/', views.home, name='home'),

    # Location management
    path('region-locations/', views.RegionLocationsListView.as_view(), name='region_locations'),
    path('region-locations/create/', views.RegionLocationsCreateView.as_view(), name='region_locations_create'),
    path('region-locations/update/<int:pk>/', views.RegionLocationsUpdateView.as_view(), name='region_locations_update'),
    path('region-locations/delete/<int:pk>/', views.RegionLocationsDeleteView.as_view(), name='region_locations_delete'),
    path('external-locations/', views.ExternalLocationsListView.as_view(), name='external_locations'),
    path('external-locations/create/', views.ExternalLocationsCreateView.as_view(), name='external_locations_create'),
    path('external-locations/update/<int:pk>/', views.ExternalLocationsUpdateView.as_view(), name='external_locations_update'),
    path('external-locations/delete/<int:pk>/', views.ExternalLocationsDeleteView.as_view(), name='external_locations_delete'),
    path('internal-locations/', views.InternalLocationsListView.as_view(), name='internal_locations'),
    path('internal-locations/create/', views.InternalLocationsCreateView.as_view(), name='internal_locations_create'),
    path('internal-locations/update/<int:pk>/', views.InternalLocationsUpdateView.as_view(), name='internal_locations_update'),
    path('internal-locations/delete/<int:pk>/', views.InternalLocationsDeleteView.as_view(), name='internal_locations_delete'),
    path('location-training-insights/', views.LocationTrainingInsightsListView.as_view(), name='location_training_insights'),
    
    # Employee management
    path('employees/', views.EmployeesListView.as_view(), name='employees'),
    path('employees/create/', views.EmployeesCreateView.as_view(), name='employees_create'),
    path('employees/create-owner/', views.EmployeesOwnerCreateView.as_view(), name='employees_create_owner'),
    path('employees/update/<int:pk>/', views.EmployeesUpdateView.as_view(), name='employees_update'),
    path('employees/update-owner/<int:pk>/', views.EmployeesOwnerUpdateView.as_view(), name='employees_update_owner'),
    path('employees/delete/<int:pk>/', views.EmployeesDeleteView.as_view(), name='employees_delete'),
    path('employees-performance/', views.EmployeesPerformanceListView.as_view(), name='employees_performance'),
    path('requests/', views.RequestsListView.as_view(), name='requests'),
    path('requests/create/', views.RequestsCreateView.as_view(), name='requests_create'),
    path('requests/update/<int:pk>/', views.RequestsUpdateView.as_view(), name='requests_update'),
    path('requests/delete/<int:pk>/', views.RequestsDeleteView.as_view(), name='requests_delete'),

    # Shift scheduling management
    path('shift-scheduling/', views.ShiftSchedulingListView.as_view(), name='shift_scheduling'),
    path('shift-scheduling/create/', views.ShiftSchedulingCreateView.as_view(), name='shift_scheduling_create'),
    path('shift-scheduling/update/<int:pk>/', views.ShiftSchedulingUpdateView.as_view(), name='shift_scheduling_update'),
    path('shift-scheduling/delete/<int:pk>/', views.ShiftSchedulingDeleteView.as_view(), name='shift_scheduling_delete'),
    path('daily-shift-records/', views.DailyShiftRecordsListView.as_view(), name='daily_shift_records'),
    path('daily-shift-records/update/<int:pk>/', views.DailyShiftRecordsUpdateView.as_view(), name='daily_shift_records_update'),
    path('weekly-shift-records/', views.WeeklyShiftRecordsListView.as_view(), name='weekly_shift_records'),
    path('break-records/', views.BreakRecordsListView.as_view(), name='break_records'),
    path('break-records/create/', views.BreakRecordsCreateView.as_view(), name='break_records_create'),
    path('break-records/update/<int:pk>/', views.BreakRecordsUpdateView.as_view(), name='break_records_update'),

    # Inventory management
    path('inventory-items/', views.InventoryItemsListView.as_view(), name='inventory_items'),
    path('inventory-items/create/', views.InventoryItemsCreateView.as_view(), name='inventory_items_create'),
    path('inventory-items/update/<int:pk>/', views.InventoryItemsUpdateView.as_view(), name='inventory_items_update'),
    path('inventory-items/delete/<int:pk>/', views.InventoryItemsDeleteView.as_view(), name='inventory_items_delete'),
    path('inventory-checks/', views.InventoryChecksListView.as_view(), name='inventory_checks'),
    path('inventory-checks/create/', views.InventoryChecksCreateView.as_view(), name='inventory_checks_create'),
    path('inventory-checks/update/<int:pk>/', views.InventoryChecksUpdateView.as_view(), name='inventory_checks_update'),
    path('inventory-checks/delete/<int:pk>/', views.InventoryChecksDeleteView.as_view(), name='inventory_checks_delete'),

    # Vendor management
    path('vendors/', views.VendorsListView.as_view(), name='vendors'),
    path('vendors/create/', views.VendorsCreateView.as_view(), name='vendors_create'),
    path('vendors/update/<int:pk>/', views.VendorsUpdateView.as_view(), name='vendors_update'),
    path('vendors/delete/<int:pk>/', views.VendorsDeleteView.as_view(), name='vendors_delete'),

    # Inventory order management
    path('orders/', views.OrdersListView.as_view(), name='orders'),
    path('orders/create/', views.OrdersCreateView.as_view(), name='orders_create'),
    path('orders/update/<int:pk>/', views.OrdersUpdateView.as_view(), name='orders_update'),
    path('order-inventory/', views.OrderInventoryListView.as_view(), name='order_inventory'),
    path('order-inventory/create/', views.OrderInventoryCreateView.as_view(), name='order_inventory_create'),
    path('order-inventory/update/<int:pk>/', views.OrderInventoryUpdateView.as_view(), name='order_inventory_update'),
    path('order-inventory-alerts/', views.OrderInventoryAlertsListView.as_view(), name='order_inventory_alerts'),

    # Task management
    path('tasks/', views.TasksListView.as_view(), name='tasks'),
    path('tasks/create/', views.TasksCreateView.as_view(), name='tasks_create'),
    path('tasks/update/<int:pk>/', views.TasksUpdateView.as_view(), name='tasks_update'),
    path('tasks/delete/<int:pk>/', views.TasksDeleteView.as_view(), name='tasks_delete'),
    path('task-comments/', views.TaskCommentsListView.as_view(), name='task_comments'),
    path('task-comments/create/', views.TaskCommentsCreateView.as_view(), name='task_comments_create'),
    path('task-comments/update/<int:pk>/', views.TaskCommentsUpdateView.as_view(), name='task_comments_update'),
    path('task-comments/delete/<int:pk>/', views.TaskCommentsDeleteView.as_view(), name='task_comments_delete'),
    path('task-alerts/', views.TaskAlertsListView.as_view(), name='task_alerts'),
    path('task-alerts/create/', views.task_alerts_create, name='task_alerts_create'),
    path('task-alerts/delete/<int:pk>/', views.TaskAlertsDeleteView.as_view(), name='task_alerts_delete'),

    # Recipe management
    path('recipes/', views.RecipesListView.as_view(), name='recipes'),
    path('recipes/create/', views.RecipesCreateView.as_view(), name='recipes_create'),
    path('recipes/update/<int:pk>/', views.RecipesUpdateView.as_view(), name='recipes_update'),
    path('recipes/delete/<int:pk>/', views.RecipesDeleteView.as_view(), name='recipes_delete'),
    path('recipe-ingredients/', views.RecipeIngredientsListView.as_view(), name='recipe_ingredients'),
    path('recipe-ingredients/create/', views.RecipeIngredientsCreateView.as_view(), name='recipe_ingredients_create'),
    path('recipe-ingredients/update/<int:pk>/', views.RecipeIngredientsUpdateView.as_view(), name='recipe_ingredients_update'),
    path('recipe-ingredients/delete/<int:pk>/', views.RecipeIngredientsDeleteView.as_view(), name='recipe_ingredients_delete'),
    
    # Menu management
    path('menu-items/', views.MenuItemsListView.as_view(), name='menu_items'),
    path('menu-items/create/', views.MenuItemsCreateView.as_view(), name='menu_items_create'),
    path('menu-items/update/<int:pk>/', views.MenuItemsUpdateView.as_view(), name='menu_items_update'),
    path('menu-items/delete/<int:pk>/', views.MenuItemsDeleteView.as_view(), name='menu_items_delete'),
    path('add-ons/', views.AddOnsListView.as_view(), name='add_ons'),
    path('add-ons/create/', views.AddOnsCreateView.as_view(), name='add_ons_create'),
    path('add-ons/update/<int:pk>/', views.AddOnsUpdateView.as_view(), name='add_ons_update'),
    path('add-ons/delete/<int:pk>/', views.AddOnsDeleteView.as_view(), name='add_ons_delete'),
    path('menu-item-add-ons/', views.MenuItemAddOnsListView.as_view(), name='menu_item_add_ons'),
    path('menu-item-add-ons/create/', views.MenuItemAddOnsCreateView.as_view(), name='menu_item_add_ons_create'),
    path('menu-item-add-ons/delete/<int:pk>/', views.MenuItemAddOnsDeleteView.as_view(), name='menu_item_add_ons_delete'),
    path('menu-item-orders/', views.MenuItemOrdersListView.as_view(), name='menu_item_orders'),
    path('menu-item-ordering-page/', views.menu_item_ordering_page, name='menu_item_ordering_page'),
    path('menu-item-orders/create/<int:menu_item_pk>/', views.MenuItemOrdersCreateView.as_view(), name='menu_item_orders_create'),
    path('menu-item-orders/update/<int:pk>/', views.MenuItemOrdersUpdateView.as_view(), name='menu_item_orders_update'),
    path('menu-engineering-reports/', views.MenuEngineeringReportsListView.as_view(), name='menu_engineering_reports'),
    path('menu-engineering-reports/create/', views.menu_engineering_report_create, name='menu_engineering_report_create'),
    path('menu-engineering-reports/delete/', views.menu_engineering_report_delete_all, name='menu_engineering_report_delete'),

    # Menu waste management
    path('waste-records/', views.WasteRecordsListView.as_view(), name='waste_records'),
    path('waste-records/create/', views.WasteRecordsCreateView.as_view(), name='waste_records_create'),
    path('waste-records/update/<int:pk>/', views.WasteRecordsUpdateView.as_view(), name='waste_records_update'),
    path('waste-records/delete/<int:pk>/', views.WasteRecordsDeleteView.as_view(), name='waste_records_delete'),
    path('waste-analysis/', views.WasteAnalysisListView.as_view(), name='waste_analysis'),
    path('waste-analysis/create/', views.waste_analysis_create, name='waste_analysis_create'),
    path('waste-analysis/delete/', views.waste_analysis_delete_all, name='waste_analysis_delete'),

    # Receipt creator + transactions log/tracker
    path('payments/', views.PaymentsListView.as_view(), name='payments'),
    path('payments/create/', views.PaymentsCreateView.as_view(), name='payments_create'),
    path('payment-receipt-print', views.payment_receipt_print, name='payment_receipt_print'),
    
    # Nutrition and allergen management
    path('nutrition-allergen-info/', views.NutritionAllergenInfoListView.as_view(), name='nutrition_allergen_info'),
    path('nutrition-allergen-info/create/', views.NutritionAllergenInfoCreateView.as_view(), name='nutrition_allergen_info_create'),
    path('nutrition-allergen-info/update/<int:pk>/', views.NutritionAllergenInfoUpdateView.as_view(), name='nutrition_allergen_info_update'),
    path('nutrition-allergen-info/delete/<int:pk>/', views.NutritionAllergenInfoDeleteView.as_view(), name='nutrition_allergen_info_delete'),

    # Inventory cost reports
    path('accounting-periods/', views.AccountingPeriodsListView.as_view(), name='accounting_reports'),
    path('accounting-periods/create/', views.AccountingPeriodsCreateView.as_view(), name='accounting_reports_create'),
    path('accounting-periods/update/<int:pk>/', views.AccountingPeriodsUpdateView.as_view(), name='accounting_reports_update'),
    path('accounting-periods/delete/<int:pk>/', views.AccountingPeriodsDeleteView.as_view(), name='accounting_reports_delete'),
    path('inventory-cost-reports/', views.InventoryCostReportsListView.as_view(), name='inventory_cost_reports'),
    path('inventory-cost-reports/create/', views.inventory_cost_report_create, name='inventory_cost_reports_create'),
    path('inventory-usage/', views.InventoryUsageListView.as_view(), name='inventory_usage'),
    path('inventory-usage/create/', views.inventory_usage_create, name='inventory_usage_create'),
    path('inventory-transfers/', views.InventoryTransfersListView.as_view(), name='inventory_transfers'),
    path('inventory-transfers/create/', views.InventoryTransfersCreateView.as_view(), name='inventory_transfers_create'),
    path('inventory-transfers/update/<int:pk>/', views.InventoryTransfersUpdateView.as_view(), name='inventory_transfers_update'),
    path('inventory-transfers/delete/<int:pk>/', views.InventoryTransfersDeleteView.as_view(), name='inventory_transfers_delete'),
    path('inventory-transfers-internal/', views.InventoryTransfersInternalListView.as_view(), name='inventory_transfers_internal'),
    path('inventory-transfers-internal/create/<int:inventory_transfer_pk>/', views.InventoryTransfersInternalCreateView.as_view(), name='inventory_transfers_internal_create'),
    path('inventory-transfers-internal/update/<int:pk>/', views.InventoryTransfersInternalUpdateView.as_view(), name='inventory_transfers_internal_update'),
    path('inventory-transfers-internal/delete/<int:pk>/', views.InventoryTransfersInternalDeleteView.as_view(), name='inventory_transfers_internal_delete'),
    path('inventory-waste-bin/', views.InventoryWasteBinListView.as_view(), name='inventory_waste_bin'),
    path('inventory-waste-bin/create/', views.InventoryWasteBinCreateView.as_view(), name='inventory_waste_bin_create'),
    path('inventory-waste-bin/update/<int:pk>/', views.InventoryWasteBinUpdateView.as_view(), name='inventory_waste_bin_update'),
    path('inventory-waste-bin/delete/<int:pk>/', views.InventoryWasteBinDeleteView.as_view(), name='inventory_waste_bin_delete'),

    # Tip management
    path('employee-tip-records/', views.EmployeeTipRecordsListView.as_view(), name='employee_tip_records'),
    path('employee-tip-records/create/', views.EmployeeTipRecordsCreateView.as_view(), name='employee_tip_records_create'),
    path('employee-tip-records/update/<int:pk>/', views.EmployeeTipRecordsUpdateView.as_view(), name='employee_tip_records_update'),
    path('tip-pooling-records/', views.TipPoolingRecordsListView.as_view(), name='tip_pooling_records'),
    path('tip-pooling-records/create/', views.TipPoolingRecordsCreateView.as_view(), name='tip_pooling_records_create'),
    path('employee-tip-payouts/', views.EmployeeTipPayoutsListView.as_view(), name='employee_tip_payouts')
]
