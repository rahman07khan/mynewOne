from .models import MasterRole,CustomUser,Categories,Product,Bought
from django.core.mail import send_mail, EmailMessage
from django.db import transaction
from django.conf import settings
from .models import MasterRole, CustomUser, Categories, Product
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password,check_password
from django.utils.crypto import get_random_string
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.core.exceptions import ValidationError
import openpyxl
from rest_framework.response import Response



User = get_user_model()



class RegisterView(APIView):
    
    def post(self, request):
        data = request.data
        name = data.get('name')
        mobile_number = data.get('mobile_number')
        email = data.get('email')
        password = data.get('password')
        role_name = data.get('role')

        if name is None or mobile_number is None or email is None or password is None or role_name is None:
            return JsonResponse({'message': 'Please provide all fields'}, status=status.HTTP_400_BAD_REQUEST)
        password_hash = make_password(password)

        transaction.set_autocommit(False)
        try:
            role = MasterRole.objects.get(role=role_name)

            register = CustomUser.objects.create(
                username=name,
                mobile_number=mobile_number,
                email=email,
                password=password_hash,
                role=role,
            )

            subject = 'Registration Successful'
            message = f'Hello {name},\n\nusername: {name}\npassword:{password}\n\nThank you!!'
            image_path = 'C:/Users/AbdulRahumankhanJaff/Downloads/thank.jpg'  # Use forward slashes in the path
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]

            try:
                email = EmailMessage(subject, message, from_email, recipient_list)
                email.attach_file(image_path)
                email.send()
                refresh = RefreshToken.for_user(register)
                response_data = {
                    'status': 'Successfully created',
                    'message': f'{role_name} of {name}, Registration Successful!!',
                    'token': str(refresh.access_token),
                }
                transaction.commit()
                return Response(response_data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                transaction.rollback()
                return JsonResponse({'error': ''}, status=status.HTTP_400_BAD_REQUEST)
        except MasterRole.DoesNotExist:
            return JsonResponse({'error': f'MasterRole {role_name} does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            transaction.rollback()
            return JsonResponse({'error': ''}, status=status.HTTP_400_BAD_REQUEST)
        


class MasterRoleView(APIView):
    def post(self, request):
        try:
            user = request.user
            if user.role.role == 'admin':
                role = request.data.get('role')
                description = request.data.get('description')
            

            try:
                existed_role = MasterRole.objects.get(role=role)
                return JsonResponse({'error': f'Role {role} already exists'}, status=status.HTTP_400_BAD_REQUEST)
            except MasterRole.DoesNotExist:
                role_instance = MasterRole(role=role,
                                        description=description,
                                        created_by=user.role.id,
                                        )
                role_instance.save()
                return JsonResponse({'message': f'Successfully created role {role}'}, status=status.HTTP_201_CREATED)
        except MasterRole.MultipleObjectsReturned:
            return JsonResponse({'error': f'Multiple roles with the same name found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    def post(self, request):
        name = request.data.get('username')
        password = request.data.get('password')
        try:
            user = CustomUser.objects.get(username=name)
        except CustomUser.DoesNotExist:
            return Response({'message': 'Invalid Username'}, status=status.HTTP_401_UNAUTHORIZED)


        if user is None or not check_password(password, user.password):
            return Response({'message': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return JsonResponse({'token': str(refresh.access_token)}, status=status.HTTP_200_OK)

class ProtectedView(APIView):

    def get(self, request):
        user = request.user
        print(user)
        register_user = CustomUser.objects.get(id=user.id)

        if register_user.role.role == 'seller':
            return JsonResponse({
                'message': f'Hello, {register_user.username}! Welcome Seller'
            })
        elif register_user.role.role == 'buyer':
            return JsonResponse({
                'message': f'Hello, {register_user.username}! Welcome Buyer'
            })
        else:
            return JsonResponse({
                'message': f'Hello, {register_user.username}! Welcome Admin'
            })

    
class SendOTP(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = CustomUser.objects.get(email=email)
        transaction.set_autocommit(False)
        otp = get_random_string(length=6, allowed_chars='0123456789')
        print(otp)
        user.otp = otp
        user.save()
        transaction.commit()

        subject = 'Your OTP Code'
        message = f'Your OTP code is: \n    {otp}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        return JsonResponse({'message': 'OTP sent successfully.'}, status=status.HTTP_200_OK)

class OTPChangePassword(APIView):
    def put(self, request):
        email = request.data.get('email')
        otp_set = request.data.get('otp')
        new_password = request.data.get('new_password')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)

        # Disable autocommit
        transaction.set_autocommit(False)

        if user.otp == otp_set:
            user.set_password(new_password)
            user.otp = ''
            user.save()

            transaction.commit()

            subject = 'Password Updated'
            message = f'Hello, your new password: {new_password} has been updated. Thank you!'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            return JsonResponse({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)
        else:
            transaction.rollback()
            return JsonResponse({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        
class SellerProcess(APIView):
    def post(self, request):
        try:
            user = request.user
            print(user)
            if user.role.role == 'seller':
                category_name = request.data.get('name')
                description = request.data.get('description')
                model_name = request.data.get('model_name')
                quantity = int(request.data.get('quantity'))
                each_price = float(request.data.get('each_price'))
                total_price = quantity * each_price

                transaction.set_autocommit(False)
                try:
                    existed_category = Categories.objects.get(name=category_name)
                    try:
                        existed_product = Product.objects.get(model_name=model_name)
                        existed_product.quantity += quantity
                        existed_product.total_price += total_price
                        existed_product.modified_user = user
                        existed_product.save()
                    except Product.DoesNotExist:
                        prod = Product(
                            model_name=model_name,
                            quantity=quantity,
                            each_price=each_price,
                            total_price=total_price,
                            category=existed_category,
                            created_user=user,
                            modified_user=user
                        )
                        prod.save()
                except Categories.DoesNotExist:
                    existed_category = Categories(
                        name=category_name,
                        description=description,
                        created_by=user,
                        modified_by=user
                    )
                    existed_category.save()
                    transaction.commit()

                return JsonResponse({'message': 'Successfully added the product'}, status=status.HTTP_201_CREATED)
            else:
                transaction.rollback()
                return JsonResponse({'error': 'Only sellers can add products.'}, status=status.HTTP_403_FORBIDDEN)
        except MasterRole.DoesNotExist:
            return JsonResponse({'error': 'Seller role not found.'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # user = request.user
        # print(user)
        # email = user.id
        # print(email)

        # if user.role.role == 'seller':
                try:
                    products = Product.objects.all()

                    html_content = render_to_string('table.html', {'products': products})

                    html_con = render_to_string('download_pdf.html', {'products': products})

                    download_pdf = request.query_params.get('download_pdf', False)

                    if download_pdf:
                        pdf_file_path = 'C:/myproject/django/pdfs/products.pdf'

                        with open(pdf_file_path, 'wb') as pdf_file:
                            pisa_status = pisa.CreatePDF(html_con, dest=pdf_file)

                        if pisa_status.err:
                            return JsonResponse({'error': 'Failed to generate PDF'}, status=status.HTTP_400_BAD_REQUEST)
                    
                        
                        

                        subject = 'PDF Downloaded'
                        message = 'Hello,\n\your selling products list is here\n\nThank you!!'
                        print(message)
                        from_email = settings.EMAIL_HOST_USER
                        recipient_list = ['abdulrahumankhan20012177@gmail.com']

                        email = EmailMessage(subject, message, from_email, recipient_list)
                        email.attach_file(pdf_file_path)
                        email.send()

                        response = HttpResponse(content_type='application/pdf')
                        response['Content-Disposition'] = f'attachment; filename="products.pdf"'
                        with open(pdf_file_path, 'rb') as pdf:
                            response.write(pdf.read())
                        return response
                    else:
                        return HttpResponse(html_content)
                
                except Product.DoesNotExist:
                    return JsonResponse({'error': 'Products not found'}, status=status.HTTP_404_NOT_FOUND)
        # else:
        #     return JsonResponse({'error': 'Only sellers can view the product list.'}, status=status.HTTP_403_FORBIDDEN)

class FeedbackUser(APIView):
    def post(self, request):
        try:
            user = request.user
            print(user)
            data = request.data
            userid = user.id
            
            # Assuming you want to extract 'categoryid' from the request data
            categoryid = data.get('categoryid')
            
            # Check if the categoryid exists in the database
            try:
                feedback_category = FeedbackCategory.objects.get(category_type=categoryid)
            except FeedbackCategory.DoesNotExist:
                return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Now you can use feedback_category in your further logic
            # For example, you can create a UserFeedbackDetails instance with this category
            # Make sure to adjust this part according to your actual use case
            user_feedback = UserFeedbackDetails.objects.create(
                userid=user.id,
                categoryid=feedback_category,
                feedback_text=data.get('feedback_text'),
                # Fill in other fields as needed
            )
            user_feedback.save()

            return Response({"message": "Feedback saved successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Handle exceptions appropriately, e.g., log them or return an error response
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class BuyerProcess(APIView):
    def put(self, request):
        try:
            user = request.user
            print(user)
            if user.role.role == 'buyer':
                product_name = request.data.get('product_name')
                quantity = int(request.data.get('quantity'))
                
                try:
                    product = Product.objects.get(model_name=product_name)
                except Product.DoesNotExist:
                    return JsonResponse({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
                
                transaction.set_autocommit(False)

                if quantity <= product.quantity:
                    total_price = quantity * product.each_price
                   
                    # buy = Bought(
                    #     product=product,
                    #     buyer=user.role.id,
                    #     quantity=quantity,
                    #     total_price=total_price
                    # )
                    # buy.save()
                    product.quantity -= quantity
                    product.save()
                    # transaction.commit()

                    return JsonResponse({
                        'message':'Thank you for Shopping'
                    }, status=status.HTTP_201_CREATED)
                else:
                    return JsonResponse({'error': 'Insufficient product quantity.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({'error': 'Only buyers can purchase products.'}, status=status.HTTP_403_FORBIDDEN)
        except MasterRole.DoesNotExist:
            return JsonResponse({'error': 'Buyer role not found.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExcelDatas(APIView):
    def post(self, request, format=None):
        try:
            excel_file = request.FILES['excel_file']
            wb = openpyxl.load_workbook(excel_file)
            ws = wb.active
            for row_number, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                model_name = row[0]
                quantity = row[1]
                each_price = row[2]
                category_id = row[4]
                missing_columns = []
                if model_name is None:
                    missing_columns.append('Model Name')
                if quantity is None:
                    missing_columns.append('Quantity')
                if each_price is None:
                    missing_columns.append('Each Price')
                if category_id is None:
                    missing_columns.append('Category ID')
                if missing_columns:
                    missing_columns_str = ''.join(missing_columns)
                    return JsonResponse({'error': f'Missing columns: {missing_columns_str} in row {row_number}'}, status=status.HTTP_400_BAD_REQUEST)
                total_price = quantity * each_price
                try:
                    category = Categories.objects.get(id=category_id)
                except Categories.DoesNotExist:
                    return JsonResponse({'error': f'Category ID "{category_id}" does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

                existed_product = Product.objects.filter(model_name=model_name).first()
                if existed_product:
                    existed_product.quantity += quantity
                    existed_product.total_price += total_price
                    existed_product.save()
                else:
                    product = Product.objects.create(
                        model_name=model_name,
                        quantity=quantity,
                        each_price=each_price,
                        total_price=total_price,
                        category=category)
            return Response({'message': 'Excel data uploaded successfully'}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CateoriesProducts(APIView):
    def get(self, request):
        categories = Categories.objects.all().values()
        data = []
        for cat in categories:
            products_list = Product.objects.filter(category=cat['id']).values()
            products_data = []
            for prod in products_list:
                products_data.append({
                    'model_name': prod['model_name'],
                    'quantity': prod['quantity'],
                    'each_price': prod['each_price'],
                    'total_price': prod['total_price']
                })
            data.append({
                'id': cat['id'],
                'name': cat['name'],
                'description': cat['description'],
                'is_active': cat['is_active'],
                'products': products_data
            })
        return JsonResponse(data, safe=False)



# class BuyersList(APIView):
#     def get(self, request):
#         data = []
#         bought_entries = Bought.objects.all()

#         for bought_entry in bought_entries:
#             product = bought_entry.product
#             product_data = {
#                 'id': product.id,
#                 'model_name': product.model_name,
#                 'each_price': product.each_price,
#             }
            
#             entry_data = {
#                 'buyer_id': bought_entry.id,
#                 'quantity': bought_entry.quantity,
#                 'total_price': bought_entry.total_price,
#                 'product': product_data,
#             }
            
#             data.append(entry_data)  

#         return Response(data)




    


