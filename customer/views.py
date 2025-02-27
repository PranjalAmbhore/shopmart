from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from seller.models import Product
from django.db.models import Q
from customer.models import Cart,Profile
from django.contrib import messages
from seller.models import Category
# Create your views here.
products=Product.objects.none()
def home(request):
    data={}
    global products
    global filtered_products
    products = Product.objects.all()
    filtered_products=products
    data['products']=products
    if(request.user.is_authenticated):
        user_id=request.user.id
        print(user_id)
        user=User.objects.get(id=user_id)
        if(user.is_staff==True):
            return redirect('/seller')
        #fetching cart count
    cart_count=Cart.objects.filter(customer_id=request.user.id).count()
    data['cart_count']= cart_count
    data['categories']=Category.objects.all()
    return render(request,'customer/base.html',context=data)

def user_register(request):
    if(request.user.is_authenticated):
        return redirect('/')
    data={}
    is_staff = False
    if(request.method == 'POST'):
        uname = request.POST.get('username')
        upass = request.POST.get('password')
        ucpass = request.POST.get('cpassword')
        utype = request.POST.get('type')
        if(utype=="seller"):
            is_staff=True
        if(uname=="" or upass=="" or ucpass==""):
            data["error_msg"]="fields cant be empty"
        elif(upass!=ucpass):
            data["error_msg"]="password does not matched"
        elif(User.objects.filter(username=uname).exists()):
            data["error_msg"]=uname+" is already exists"
        else:
            user=User.objects.create(username=uname,is_staff=is_staff)
            user.set_password(upass)
            user.save()
            return redirect("/login")
        
    return render(request,'customer/register.html',context=data)

def user_login(request):
    if(request.user.is_authenticated):
        return redirect('/')
    data={}
    if(request.method == 'POST'):
        uname = request.POST.get('username')
        upass = request.POST.get('password')
        utype = request.POST.get('type')
        if(uname=="" or upass==""):
            data["error_msg"]="fields cant be empty"
        elif(not User.objects.filter(username=uname).exists()):
            data["error_msg"]=uname+" is already exists"
        else:
            authenticated_user=authenticate(username=uname, password=upass)
            if(authenticated_user is None):
                data["error_msg"]="Incorrect password"
            else:
                login(request,authenticated_user)
                if(authenticated_user.is_staff):
                    print("seller")
                    return redirect("/seller")
                else:
                    print("customer")
                    return redirect("/")
           
    return render(request,'customer/login.html',context=data)

def user_logout(request):
    logout(request)
    return redirect("/")

def add_to_cart(requset,product_id):
    if(requset.user.is_authenticated):
        q1 = Q(customer_id=requset.user.id)
        q2 = Q(product_id= product_id)
        cart_items=Cart.objects.filter(q1 & q2)
        if(cart_items.count()>=1):
            messages.error(requset, "Product is already in the cart")
            return redirect ("/")
        else:
            customer = User.objects.get(id=requset.user.id)
            product = Product.objects.get(id=product_id)
            created_cart=Cart.objects.create(quantity=1, customer_id=customer,product_id=product)
            created_cart.save()
            messages.success(requset, "Product added to the cart")
            return redirect("/")
    else:
        return redirect("/")

def view_cart(request):
    data={}
    cart_items=Cart.objects.filter(customer_id=request.user.id)
    quantity=0
    total_price=0
    for item in cart_items:
        quantity+=item.quantity
        total_price+=(item.quantity*item.product_id.price)
    data['quantity']=quantity
    data['total_price']=total_price
    data['cart_count']=cart_items.count()
    data['products']=cart_items
    return render(request,'customer/cart.html',context=data)

def delete_cart_item(request, cart_id):
    cart_item=Cart.objects.get(id=cart_id)
    cart_item.delete()
    return redirect("/cart")

def update_cart(request,flag,cart_id):
    cart_items=Cart.objects.filter(id=cart_id)
    actual_quantity=cart_items[0].quantity
    if(flag=="inc"):
        cart_items.update(quantity=actual_quantity+1)
    else:
        if(actual_quantity==1):
            pass
        else:
           cart_items.update(quantity=actual_quantity-1) 
    print(flag)
    return redirect ("/cart")

def filterByCategory(request,categoryId):
    data={}
    global products
    global filtered_products
    filtered_products=products.filter(category_id=categoryId)
    data['products']=filtered_products
    data['categories']=Category.objects.all()
    return render(request,'customer/base.html',context=data)

def sortByPrice(request,flag):
    data={}
    global filtered_products
    if(flag=="high-to-low"):
        sorted_products=filtered_products.order_by("-price")
        data['products']=sorted_products
        data['categories']=Category.objects.all()
        return render(request,'customer/base.html',context=data)
    else:
        sorted_products=filtered_products.order_by("price")
        data['products']=sorted_products
        data['categories']=Category.objects.all()
        return render(request,'customer/base.html',context=data)

def searchByName(request):
    data={}
    global filtered_products
    if(request.method == 'POST'):
        product_name=request.POST.get('product_name')
        print(product_name)
        searched_products=filtered_products.filter(name__icontains=product_name)
        data['products']=searched_products
        data['categories']=Category.objects.all()
        return render(request,'customer/base.html',context=data)
    return redirect("/")

def filteredByPriceRange(request):
    data={}
    global filtered_products
    if(request.method=="POST"):
        min=request.POST.get("min")
        max=request.POST.get("max")
        q1=Q(price__gte=min)
        q2=Q(price__lte=max)
        filtered_by_price_range = filtered_products.filter(q1 & q2)
        data['products']=filtered_by_price_range
        data['categories']=Category.objects.all()
        return render(request,'customer/base.html',context=data)
    return redirect("/")

def updateProfile(request):
    data={}
    user=User.objects.filter(id=request.user.id)
    if(request.method == "POST"):
        firstname=request.POST.get("firstname")
        lastname=request.POST.get("lastname") 
        email=request.POST.get("email")
        contact=request.POST.get("contact")
        street=request.POST.get("street")
        city=request.POST.get("city")
        state=request.POST.get("state")
        pincode=request.POST.get("pincode")
        user.update(first_name=firstname,last_name=lastname,email=email)
        if(Profile.objects.filter(user_id=request.user.id).exists()):
            existing_profile = Profile.objects.filter(user_id=request.user.id)          
            existing_profile.update(contact=contact,street=street,city=city,state=state,pincode=pincode)
        else:
            user_object = User.objects.get(id=request.user.id)
            new_profile=Profile.objects.create(contact=contact,street=street,city=city,state=state,pincode=pincode,user_id=user_object)
            new_profile.save()
        return redirect("/profile")
    cart_count=Cart.objects.filter(customer_id=request.user.id).count()
    data['cart_count']=cart_count
    userx=User.objects.get(id=request.user.id)
    profilex=Profile.objects.filter(user_id=userx)
    if(not userx.first_name and  profilex.count()==0):
        print("data does not exist")
    else:
        data['user'] = userx
        data['address'] = profilex[0]
        return render(request, 'customer/profile.html',context=data)
    return render(request, 'customer/profile.html',context=data)
        
def order_summary(request):
   data={}
   cart_items=Cart.objects.filter(customer_id=request.user.id)
   quantity=0
   total_price=0
   for item in cart_items:
      quantity+=item.quantity
      total_price += (item.quantity * item.product_id.price)
   data['quantity'] =quantity
   data['total_price'] =total_price
   data['cart_count']=cart_items.count()
   data['cart_items'] = cart_items
   
   address=Profile.objects.filter(user_id=request.user.id)
   data['address'] = address[0]

   
   import razorpay


   client = razorpay.Client(auth=("rzp_test_xr6Py3IFJai7lm", "237ZMwl1cXS89rrf6NEx4bFR"))
   payment_data = { "amount": total_price, "currency": "INR", "receipt": "order_rcptid_11" }
   payment = client.order.create(data=payment_data)

   return render(request,'customer/order_summary.html',context=data)