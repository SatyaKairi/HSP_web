from django.forms import ValidationError
from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from api.forms import ResetPasswordForm
from .serializers import *
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated,AllowAny 
from rest_framework import status
from typing import Any
from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework.decorators import action, api_view, permission_classes
from datetime import date, datetime
from rest_framework import viewsets
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
import uuid
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView
from django.db.models import Sum,Max
from django.utils.timezone import now



# def authenticate(request: Any = ..., **credentials: Any) -> AbstractBaseUser | None: ...

# Create your views here.
@permission_classes([IsAuthenticated])
class DonationViewSet(viewsets.ModelViewSet):
    serializer_class = DonationSerializer

    def get_queryset(self):
        receipt_from = self.request.query_params.get('receipt_from')
        receipt_to = self.request.query_params.get('receipt_to')
        searchQuery = self.request.query_params.get('searchQuery')
        
        user = self.request.user
        queryset = Donation.objects.all()
        print(user)
        if user:
            if not user.is_admin:
                # Non-admin users should only see their institution and branch
                print('user_is_not_admin')
                queryset = queryset.filter(
                    Q(institution=user.institution, institutionBranch=user.institutionBranch,created_by=user)
                )
        else:
            print('user_is_admin')
            print(user.institution)
            queryset = queryset.filter(
                Q(institution=user.institution)
            )
            print(queryset)

        if receipt_from and receipt_to:
            print("Have Dates")
            # Apply time filter
            receipt_from_date = datetime.strptime(receipt_from, '%Y-%m-%d').date()
            receipt_to_date = datetime.strptime(receipt_to, '%Y-%m-%d').date()

            if searchQuery:
                # Apply additional search query filter
                queryset = queryset.filter(
                    Q(date_receipt__gte=receipt_from_date) &
                    Q(date_receipt__lte=receipt_to_date) &
                    (Q(donation_receipt__icontains=searchQuery) | Q(received_from__icontains=searchQuery))
                )
            else:
                queryset = queryset.filter(Q(date_receipt__gte=receipt_from_date) & Q(date_receipt__lte=receipt_to_date))
        elif searchQuery:
            print("Have Search Queries")
            # Only apply search query filter if no time filter is present
            queryset = queryset.filter(
                (Q(donation_receipt__icontains=searchQuery) | Q(received_from__icontains=searchQuery))
            )
        queryset = queryset.select_related('donor')
        queryset = queryset.order_by('-created_date')
        return queryset

class UserLoginAPIView(APIView):
    print("Coming here")
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        print(username, password)
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(user)
            context={
                "token": token.key,
                "user" : serializer.data,
                
                
            }
            
            return Response(context, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    
@permission_classes([IsAuthenticated])
class DonorCreateView(generics.CreateAPIView):
    
    # serializer_class = DonorSerializer
    def create(self, request, *args, **kwargs):
    # Extract donor-related data from the request
        donor_data = {
            'name': request.data.get('donorName'),
            'email_id': request.data.get('donorEmail'),
            'phone_no': request.data.get('donorPhoneNumber'),
            'home_address': request.data.get('donorHomeAddress'),
            'pan_card_no': request.data.get('donorPAN'),
            'adhaar_no': request.data.get('donorAadhar'),
            'donor_photo': request.data.get('donorPhoto'),
        }
        print(donor_data)

        # Check if the donor number is already taken
        donor_number = donor_data['phone_no']
        print(donor_number)
        if Donor.objects.filter(phone_no=donor_number).exists():
            return Response(
                {'error': f'Donor with phone number {donor_number} already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        print("Coming here")
        
        # Validate and save the donor
        serializer = DonorSerializer(data=donor_data)
        print(serializer.is_valid())
        if serializer.is_valid():
            serializer.save()  # Save the donor
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            first_error_message = next(iter(serializer.errors.values()))[0]
            return Response({'error': first_error_message}, status=status.HTTP_400_BAD_REQUEST)
    
@permission_classes([IsAuthenticated])
class DonationAPIView(APIView):
    def perform_create(self, serializer):
        
        donation = serializer.save()
        
        # Get the latest donation number for the current institution branch
        latest_donation_number = Donation.objects.filter(
            institutionBranch=donation.institutionBranch
        ).aggregate(Max('donation_number'))['donation_number__max'] or 0
        
        donation_number = latest_donation_number + 1
        
        # Generate unique donation_receipt based on current donation_number and institution_branch name
        donation_receipt = f"{donation.institutionBranch.name}_{str(donation_number).zfill(5)}"
        
        donation.donation_number = donation_number
        donation.donation_receipt = donation_receipt
        donation.save()

    def post(self, request, *args, **kwargs):
        user = request.user  # Assuming you are using TokenAuthentication
        
        institution_branch = user.institutionBranch

        # Check if the branch has a monthly invoice limit
        monthly_invoice_limit = institution_branch.monthly_invoice_limit
        print(monthly_invoice_limit)
        if monthly_invoice_limit is not None:
            # Get the current month and year
            current_month = now().month
            current_year = now().year
            print("Coming to monthly invoice limit check")
            # Count the invoices generated for the current month
            current_month_invoice_count = Donation.objects.filter(
                institutionBranch=institution_branch,
                created_date__year=current_year,
                created_date__month=current_month
                
            ).count()
            print(current_month_invoice_count)
            
            # Check if the count exceeds the monthly limit
            if current_month_invoice_count > monthly_invoice_limit:
                return Response(
                    {'message': ' Monthly invoice limit exceeded for this branch.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
                

        # Extract donor-related data from the request
        donor_data = {
            'name': request.data.get('donorName'),
            'email_id': request.data.get('donorEmail'),
            'phone_no': request.data.get('donorPhoneNumber'),
            'home_address': request.data.get('donorHomeAddress'),
            'pan_card_no': request.data.get('donorPAN'),
            'adhaar_no': request.data.get('donorAadhar'),
            'donor_photo': request.data.get('donorPhoto')  # Adjust as needed
        }
        
        try:
            donor = Donor.objects.get(phone_no=donor_data['phone_no'])
        except Donor.DoesNotExist:
            donor = Donor.objects.create(**donor_data)
        except Donor.MultipleObjectsReturned:
            donor = Donor.objects.filter(phone_no=donor_data['phone_no']).first()
            
        print(donor)
            
        request_data = request.data.copy()
        request_data['created_by'] = user.id
        request_data['institution'] = user.institution.id
        request_data['institutionBranch'] = user.institutionBranch.id
        
        request_data['donor'] = donor.id  # Associate the donor with the donation
        
        # Add the new fields to the request data
        request_data['describe_towards'] = request.data.get('Describe_towards', '')
        request_data['transaction_details'] = request.data.get('transaction_details', '')
        request_data['other_product_details'] = request.data.get('other_product_details', '')
        request_data['quantity_unit'] = request.data.get('quantity_unit', '')
        
        

        serializer = DonationSerializer(data=request_data)
        # Ensure the institutionBranch was correctly set
        
        institution_branch_id = request_data.get('institutionBranch')
        institution_branch = get_object_or_404(InstitutionBranch, id=institution_branch_id)
        
        if serializer.is_valid():
            
            self.perform_create(serializer)
            passing_data = serializer.data
            passing_data['donorName'] = donor_data['name']
            passing_data['address'] = donor_data['home_address']
            passing_data['phone'] = donor_data['phone_no']
            passing_data['email'] = donor_data['email_id']
            passing_data['pan'] = donor_data['pan_card_no']
            passing_data['institution_branch_name'] = institution_branch.name
            passing_data['institution_phone_no'] = institution_branch.phone_no   
            return Response({'donation':passing_data}, status=status.HTTP_201_CREATED)
        
        print("Validation Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class ForgotPasswordView(APIView):
    
    
    def post(self, request):
        email = request.data.get('email')
        print("here is the email" + email)
        try:
            user = DhaanaDonationUsers.objects.get(email=email)
        except Exception as e:
            print(e)
            print("Coming here ")
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    

        # Generate a unique token
        token = str(uuid.uuid4())
        password_reset = PasswordReset.objects.create(user=user, token=token)
        
        # Send email with reset link
        reset_link = f"https://gyan.center/hsp_web/api/reset-password/{token}/"
        # reset_link = f"http://127.0.0.1:8000/api/reset-password/{token}/"
        send_mail(
            'Password Reset',
            f'Click the following link to reset your password for username {user.username}: {reset_link}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return Response({'message': 'Password reset email sent successfully'}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    def get(self, request, token):
        form = ResetPasswordForm()
        return render(request, 'reset_password.html', {'form': form, 'token': token})
    def post(self, request, token):
        try:
            password_reset = PasswordReset.objects.get(token=token)
        except PasswordReset.DoesNotExist:
            return render(request, 'response.html', {'error': 'Invalid or expired token'})

        new_password = request.data.get('new_password')
        password_reset.user.set_password(new_password)
        password_reset.user.save()

        # Delete the password reset record
        password_reset.delete()

        return render(request, 'response.html', {'message': 'Password reset successful, Please Use this new password to access Dhaana Donation'})
    
class InstitutionGalaryAPIView(generics.ListAPIView):
    serializer_class = InstitutionGalarySerializer
    
    def get_queryset(self):
        institution_id = self.kwargs['institution_id']
        print(institution_id)
        try:
            institution = get_object_or_404(Institution, id=institution_id)
            institution_galary = InstitutionGalary.objects.filter(institution=institution)
            return institution_galary
        except Exception as e:
            # Log the exception or handle it based on your requirements
            print(e)
            return None
        
class FoodInventoryListAPIView(generics.ListCreateAPIView):
    queryset = FoodInventoryList.objects.all()
    serializer_class = FoodInventoryListSerializer
    
    
    
class DonorDetailsAPIView(RetrieveAPIView):
    serializer_class = DonorSerializer

    def get(self, request, *args, **kwargs):
        phone_no = request.query_params.get('phone_no', None)
        if phone_no is None:
            return Response({'error': 'Phone number not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            donor = Donor.objects.filter(phone_no=phone_no).first()
            if donor:
                serializer = self.get_serializer(donor)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Donor not found'}, status=status.HTTP_404_NOT_FOUND)    
        except Donor.DoesNotExist:
            return Response({'error': 'Donor not found'}, status=status.HTTP_404_NOT_FOUND)
    

class BranchListAPIView(generics.ListAPIView):
    serializer_class = InstitutionBranchSerializer
    
    def get_queryset(self):
        institution_id = self.kwargs['institution_id']
        institution = get_object_or_404(Institution, id=institution_id)
        branches = InstitutionBranch.objects.filter(institution=institution)
        for b in branches:
            print(b.image)
        # serializer = InstitutionBranchSerializer(branches, many=True)
        # return Response(branches, status=status.HTTP_200_OK) 
        return branches
    
class BranchDetailView(APIView):
    def get(self, request, branch_id):
        branch = get_object_or_404(InstitutionBranch, id=branch_id)
        
        # Get assets and their quantities
        assets = InstitutionBranchAsset.objects.filter(institution_branch__id=branch_id)
        asset_data = InstitutionBranchAssetSerializer(assets, many=True).data
        
        # Calculate total revenue from donations
        total_revenue = Donation.objects.filter(institutionBranch__id=branch_id).aggregate(total_revenue=Sum('received_amount'))['total_revenue'] or 0

        # Calculate total donations of type Goods
        total_goods_donations = Donation.objects.filter(institutionBranch__id=branch_id, donation_form='goods').count()
        total_donation  = Donation.objects.filter(institutionBranch__id=branch_id).count()

        # Serialize the data
        branch_serializer = BranchDetailSerializer(branch)
        stats_serializer = BranchStatsSerializer({'total_revenue': total_revenue, 'total_goods_donations': total_goods_donations,'total_donation':total_donation})

        return Response({
            'branch': branch_serializer.data,
            'assets': asset_data,
            'stats': stats_serializer.data
        }, status=status.HTTP_200_OK)
        
def privacy_policy(request):
    return render(request, 'privacy-policy.html')


class DonationDetailsAPIView(generics.RetrieveAPIView):
    serializer_class = DonationSerializer
    queryset = Donation.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Retrieve institution name and branch name instead of IDs
        data['institution'] = instance.institution.name if instance.institution else None
        data['institution_branch'] = instance.institutionBranch.name if instance.institutionBranch else None
        data['donor'] = instance.donor.name if instance.donor else None
        data['donor_email'] = instance.donor.email_id if instance.donor else None
        data['donor_phone'] = instance.donor.phone_no if instance.donor else None
        data['created_by'] = instance.created_by.username if instance.created_by else None
        data['donor_address'] = instance.donor.home_address if instance.donor else None
        data['pan'] = instance.donor.pan_card_no if instance.donor else None
        
        return Response(data)